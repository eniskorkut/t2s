import pandas as pd
import traceback
from typing import List, Dict

class ScannerService:
    """
    Service to scan database for categorical values and train Vanna with them.
    This helps the RAG system understand specific entity names that exist in the DB.
    """
    
    @staticmethod
    def get_text_columns(vn) -> List[Dict]:
        """
        Get all text/varchar columns from the database.
        """
        # PostgreSQL specific query for information_schema
        sql = """
        SELECT table_name, column_name 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
          AND data_type IN ('character varying', 'text', 'char', 'character')
        """
        
        try:
            df = vn.run_sql(sql)
            if df is not None and not df.empty:
                return df.to_dict(orient='records')
            return []
        except Exception as e:
            print(f"Error getting columns: {e}")
            return []

    @staticmethod
    def is_categorical(vn, table: str, column: str, max_distinct=50) -> bool:
        """
        Check if a column is categorical (has few distinct values).
        """
        try:
            sql = f'SELECT COUNT(DISTINCT "{column}") as cnt FROM "{table}"'
            df = vn.run_sql(sql)
            if df is not None and not df.empty:
                count = int(df.iloc[0]['cnt'])
                return 1 < count <= max_distinct
            return False
        except Exception as e:
            print(f"Error checking cardinality for {table}.{column}: {e}")
            return False

    @staticmethod
    def get_distinct_values(vn, table: str, column: str, limit=50) -> List[str]:
        """
        Get distinct values for a column.
        """
        try:
            sql = f'SELECT DISTINCT "{column}" FROM "{table}" LIMIT {limit}'
            df = vn.run_sql(sql)
            if df is not None and not df.empty:
                # Filter out None/Null/Empty
                values = df.iloc[:, 0].dropna().astype(str).tolist()
                return [v for v in values if v.strip()]
            return []
        except Exception as e:
            print(f"Error getting values for {table}.{column}: {e}")
            return []

    
    # Track status
    _last_run = None
    _next_run = None
    _is_running = False

    @classmethod
    def get_status(cls):
        return {
            "last_run": cls._last_run,
            "next_run": cls._next_run,
            "is_running": cls._is_running
        }

    @classmethod
    def set_next_run(cls, dt):
        cls._next_run = dt

    @staticmethod
    def scan_and_train(vn):
        """
        Main method to scan DB and train Vanna with values.
        """
        if ScannerService._is_running:
            print("⏳ [Data Scanner] Scan already in progress, skipping...")
            return {"success": False, "message": "Scan already in progress"}

        try:
            ScannerService._is_running = True
            import datetime
            print("🔍 [Data Scanner] Starting automatic data scan...")
            
            # 1. Get candidate columns
            columns = ScannerService.get_text_columns(vn)
            print(f"📊 [Data Scanner] Found {len(columns)} text columns to analyze")
            
            trained_count = 0
            skipped_cols = ['id', 'email', 'password', 'token', 'slug', 'url', 'image', 'file', 'path', 'hash', 'uuid', 'created_at', 'updated_at']
            
            for col_info in columns:
                table = col_info.get('table_name')
                column = col_info.get('column_name')
                
                # Skip if table or column is missing
                if not table or not column:
                    continue
                    
                # Skip sensitive or irrelevant columns
                if any(skip in column.lower() for skip in skipped_cols):
                    continue
                    
                print(f"   👉 Checking {table}.{column}...")
                
                # 2. Check cardinality
                if ScannerService.is_categorical(vn, table, column):
                    # 3. Get values
                    values = ScannerService.get_distinct_values(vn, table, column)
                    
                    if values:
                        # 4. Train Vanna
                        doc_content = f"Valid values for table '{table}' column '{column}': {', '.join(values)}"
                        
                        try:
                            # Optional: Remove old documentation for this column if possible to avoid duplicates
                            # But Vanna doesn't support easy deletion by metadata yet, so we just add new.
                            # RAG will pick the most relevant.
                            
                            vn.train(documentation=doc_content)
                            print(f"      ✅ Trained: {table}.{column} ({len(values)} values)")
                            trained_count += 1
                        except Exception as e:
                            print(f"      ❌ Failed to train {table}.{column}: {e}")
                else:
                    print(f"      Running... (Not categorical or too many values)")

            print(f"🏁 [Data Scanner] Scan completed. Trained {trained_count} new categorical columns.")
            
            ScannerService._last_run = datetime.datetime.now().isoformat()
            return {"success": True, "trained_count": trained_count}
        
        except Exception as e:
            print(f"❌ [Data Scanner] Critical Failure: {e}")
            traceback.print_exc()
            return {"success": False, "error": str(e)}
        finally:
            ScannerService._is_running = False
