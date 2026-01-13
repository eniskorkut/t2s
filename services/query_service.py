"""
Query Service - Single Responsibility: Saved query operations.
SOLID: Single Responsibility Principle
"""
from typing import List, Optional, Dict, Any
import pandas as pd
import json
from .database_service import DatabaseService


class QueryService:
    """Service for handling saved query operations."""
    
    def __init__(self, db_service: DatabaseService):
        """
        Initialize query service.
        
        Args:
            db_service: DatabaseService instance
        """
        self.db_service = db_service
    
    def save_query(
        self,
        user_id: int,
        question: str,
        sql_query: str,
        is_trained: bool = False
    ) -> Optional[int]:
        """
        Save a user query.
        
        Args:
            user_id: User ID
            question: User's question
            sql_query: Generated SQL query
            is_trained: Whether query was used for training
            
        Returns:
            Query ID if successful, None otherwise
        """
        query = """
            INSERT INTO user_saved_queries (user_id, question, sql_query, is_trained)
            VALUES (?, ?, ?, ?)
        """
        
        try:
            query_id = self.db_service.execute_insert(
                query,
                (user_id, question, sql_query, 1 if is_trained else 0)
            )
            return query_id
        except Exception:
            return None
    
    def get_user_queries(self, user_id: int) -> List[Dict]:
        """
        Get all saved queries for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of query dictionaries
        """
        query = """
            SELECT id, question, sql_query, saved_at, is_trained
            FROM user_saved_queries
            WHERE user_id = ?
            ORDER BY saved_at DESC
        """
        
        results = self.db_service.execute_query(query, (user_id,))
        return results
    
    def get_query_by_id(self, query_id: int, user_id: int) -> Optional[Dict]:
        """
        Get a specific query by ID (ensuring it belongs to user).
        
        Args:
            query_id: Query ID
            user_id: User ID (for security)
            
        Returns:
            Query dictionary or None if not found/not owned by user
        """
        query = """
            SELECT id, question, sql_query, saved_at, is_trained
            FROM user_saved_queries
            WHERE id = ? AND user_id = ?
        """
        
        results = self.db_service.execute_query(query, (query_id, user_id))
        
        if results:
            return results[0]
        return None
    
    def delete_query(self, query_id: int, user_id: int) -> bool:
        """
        Delete a query (ensuring it belongs to user).
        
        Args:
            query_id: Query ID
            user_id: User ID (for security)
            
        Returns:
            True if deleted, False otherwise
        """
        query = "DELETE FROM user_saved_queries WHERE id = ? AND user_id = ?"
        
        try:
            rows_affected = self.db_service.execute_update(query, (query_id, user_id))
            return rows_affected > 0
        except Exception:
            return False
    
    def mark_as_trained(self, query_id: int, user_id: int) -> bool:
        """
        Mark a query as trained.
        
        Args:
            query_id: Query ID
            user_id: User ID (for security)
            
        Returns:
            True if updated, False otherwise
        """
        query = """
            UPDATE user_saved_queries
            SET is_trained = 1
            WHERE id = ? AND user_id = ?
        """
        
        try:
            rows_affected = self.db_service.execute_update(query, (query_id, user_id))
            return rows_affected > 0
        except Exception:
            return False
    
    @staticmethod
    def check_semantic_cache(vn, question: str, threshold: float = 0.3) -> Optional[str]:
        """
        Check semantic cache for similar questions.
        Uses ChromaDB vector store to find similar questions and return cached SQL.
        
        Args:
            vn: Vanna instance with vector store
            question: User's question
            threshold: Maximum distance threshold (default 0.3)
            
        Returns:
            Cached SQL string if similar question found, None otherwise
        """
        try:
            # Check if vn has sql_collection (ChromaDB_VectorStore)
            if not hasattr(vn, 'sql_collection'):
                return None
            
            # Query ChromaDB for similar questions
            results = vn.sql_collection.query(
                query_texts=[question],
                n_results=1,
                include=["metadatas", "distances", "documents"]
            )
            
            # Check if results exist and distance is below threshold
            if results.get('distances') and len(results['distances']) > 0:
                if len(results['distances'][0]) > 0:
                    distance = results['distances'][0][0]
                    if distance < threshold:
                        # Try to extract from documents (ChromaDB stores JSON strings)
                        if results.get('documents') and len(results['documents']) > 0:
                            try:
                                doc = results['documents'][0][0]
                                if isinstance(doc, str):
                                    doc_dict = json.loads(doc)
                                    if 'sql' in doc_dict:
                                        return doc_dict['sql']
                            except (json.JSONDecodeError, KeyError):
                                pass
        except Exception as e:
            print(f"Warning: Semantic cache check failed: {e}")
            return None
        
        return None
    
    @staticmethod
    def validate_sql_safety(sql: str) -> bool:
        """
        Validate SQL for safety.
        Prevent dangerous operations like DROP, DELETE, etc.
        
        Args:
            sql: SQL string to validate
            
        Returns:
            True if safe, False otherwise
            
        Raises:
            ValueError: If SQL contains forbidden keywords
        """
        forbidden_keywords = [
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'TRUNCATE', 'GRANT', 'REVOKE', 'EXEC'
        ]
        
        sql_upper = sql.upper()
        
        for keyword in forbidden_keywords:
            # Kelime sınırlarını kontrol et (örn: update_date geçerli olmalı, sadece UPDATE değil)
            # Basit kontrol: Boşlukla çevrili veya string başında/sonunda
            if f" {keyword} " in f" {sql_upper} ":
                raise ValueError(f"Güvenlik İhlali: '{keyword}' komutu bu sistemde yasaklanmıştır.")
        
        return True

    @staticmethod
    def generate_plotly_chart(df: pd.DataFrame, sql: str) -> Optional[Dict[str, Any]]:
        """
        DataFrame'den otomatik olarak uygun Plotly grafiği oluşturur.
        
        Args:
            df: Pandas DataFrame
            sql: SQL sorgusu (grafik tipini belirlemek için kullanılır)
            
        Returns:
            Plotly JSON formatında grafik verisi veya None
        """
        try:
            # Eğer veri yoksa veya çok fazla satır varsa grafik oluşturma
            if df.empty or len(df) > 100:
                return None
            
            # Sütun sayısı 1 ise grafik oluşturma
            if len(df.columns) < 2:
                return None
            
            import plotly.graph_objects as go
            
            # İlk sütun genellikle kategori/label, diğerleri değerler
            columns = df.columns.tolist()
            x_col = columns[0]
            
            # Sayısal sütunları bul
            numeric_columns = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
            
            if not numeric_columns:
                return None
            
            # SQL'den grafik tipini tahmin et
            sql_lower = sql.lower()
            
            # Grafik oluştur
            fig = go.Figure()
            
            # Eğer tek bir sayısal sütun varsa, basit bar chart
            if len(numeric_columns) == 1:
                y_col = numeric_columns[0]
                
                # DataFrame verilerini liste olarak al - STRING OLARAK!
                # Bu çok önemli: Plotly'nin kategorik verileri düzgün göstermesi için
                x_data = df[x_col].astype(str).tolist()
                y_data = df[y_col].tolist()
                
                # Debug: Hangi veri gönderiliyor?
                print(f"Chart Debug - X data (categories): {x_data}")
                print(f"Chart Debug - Y data (values): {y_data}")
                print(f"Chart Debug - X column: {x_col}, Y column: {y_col}")
                
                # COUNT, SUM gibi agregasyon varsa bar chart
                if any(keyword in sql_lower for keyword in ['count', 'sum', 'avg', 'average']):
                    # Değerleri formatlı string olarak hazırla
                    text_values = [f'{val:,.0f}' if val > 100 else f'{val:.2f}' for val in y_data]
                    
                    fig.add_trace(go.Bar(
                        x=x_data,
                        y=y_data,
                        name=y_col,
                        marker_color='rgb(55, 83, 109)',
                        text=text_values,  # Formatlanmış değerleri göster
                        textposition='outside',
                        textfont=dict(size=10),
                        hovertemplate='<b>%{x}</b><br>' + y_col + ': %{y:,.2f}<extra></extra>'
                    ))
                    chart_type = 'bar'
                
                # ORDER BY salary DESC gibi sıralama varsa, horizontal bar
                elif 'order by' in sql_lower and any(word in sql_lower for word in ['desc', 'salary', 'price', 'amount']):
                    text_values = [f'{val:,.0f}' if val > 100 else f'{val:.2f}' for val in y_data]
                    
                    fig.add_trace(go.Bar(
                        x=y_data,
                        y=x_data,
                        orientation='h',
                        name=y_col,
                        marker_color='rgb(26, 118, 255)',
                        text=text_values,
                        textposition='outside',
                        textfont=dict(size=10),
                        hovertemplate='<b>%{y}</b><br>' + y_col + ': %{x:,.2f}<extra></extra>'
                    ))
                    chart_type = 'horizontal_bar'
                
                # Varsayılan: bar chart
                else:
                    text_values = [f'{val:,.0f}' if val > 100 else f'{val:.2f}' for val in y_data]
                    
                    fig.add_trace(go.Bar(
                        x=x_data,
                        y=y_data,
                        name=y_col,
                        marker_color='rgb(55, 83, 109)',
                        text=text_values,
                        textposition='outside',
                        textfont=dict(size=10),
                        hovertemplate='<b>%{x}</b><br>' + y_col + ': %{y:,.2f}<extra></extra>'
                    ))
                    chart_type = 'bar'
            
            # Birden fazla sayısal sütun varsa, grouped bar chart veya line chart
            else:
                # DataFrame verilerini liste olarak al - STRING OLARAK!
                x_data = df[x_col].astype(str).tolist()
                
                # Tarih sütunu varsa line chart
                date_columns = df.select_dtypes(include=['datetime64']).columns.tolist()
                if date_columns or any(word in x_col.lower() for word in ['date', 'time', 'year', 'month']):
                    for y_col in numeric_columns[:3]:  # Max 3 seri
                        y_data = df[y_col].tolist()
                        fig.add_trace(go.Scatter(
                            x=x_data,
                            y=y_data,
                            mode='lines+markers',
                            name=y_col,
                            hovertemplate='<b>%{x}</b><br>%{y:,.2f}<extra></extra>'
                        ))
                    chart_type = 'line'
                else:
                    # Grouped bar chart
                    for y_col in numeric_columns[:3]:  # Max 3 seri
                        y_data = df[y_col].tolist()
                        fig.add_trace(go.Bar(
                            x=x_data,
                            y=y_data,
                            name=y_col,
                            hovertemplate='<b>%{x}</b><br>%{fullData.name}: %{y:,.2f}<extra></extra>'
                        ))
                    chart_type = 'grouped_bar'
            
            # Layout ayarları
            fig.update_layout(
                title=dict(
                    text='Sorgu Sonuçları',
                    x=0.5,
                    xanchor='center',
                    font=dict(size=16, color='black')
                ),
                xaxis_title=dict(
                    text=x_col.replace('_', ' ').title(),
                    font=dict(size=13, color='black')
                ),
                yaxis_title=dict(
                    text=(numeric_columns[0] if len(numeric_columns) == 1 else 'Değer').replace('_', ' ').title(),
                    font=dict(size=13, color='black')
                ),
                hovermode='closest',
                showlegend=len(numeric_columns) > 1,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(
                    family="Arial, sans-serif",
                    size=12,
                    color="black"
                ),
                margin=dict(l=70, r=50, t=70, b=80),  # Arttırılmış margin'ler
                height=450,  # Biraz daha yüksek
                bargap=0.2  # Bar'lar arası boşluk
            )
            
            # X ekseni ayarları - etiketleri düzgün göster
            fig.update_xaxes(
                showgrid=True, 
                gridwidth=1, 
                gridcolor='rgba(200, 200, 200, 0.5)',
                tickangle=0,  # Yatay tut
                type='category',  # Kategorik veri olarak işle - ÖNEMLİ!
                categoryorder='trace',  # Veri sırasını koru
                tickmode='linear',  # Tüm değerleri göster
                tickfont=dict(size=11, color='black'),
                showline=True,
                linewidth=1,
                linecolor='lightgray',
                automargin=True  # Otomatik margin ayarla
            )
            
            # Y ekseni ayarları
            fig.update_yaxes(
                showgrid=True, 
                gridwidth=1, 
                gridcolor='rgba(200, 200, 200, 0.5)',
                tickfont=dict(size=11, color='black'),
                showline=True,
                linewidth=1,
                linecolor='lightgray',
                rangemode='tozero'  # 0'dan başlat
            )
            
            # Convert to JSON-serializable dict
            plotly_dict = fig.to_dict()
            
            # Convert to JSON and back to ensure it's fully serializable
            # This handles NumPy types and other non-JSON types
            json_str = json.dumps(plotly_dict, default=str)
            return json.loads(json_str)
            
        except Exception as e:
            print(f"Warning: Failed to generate chart: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def should_generate_chart(df: pd.DataFrame, sql: str) -> bool:
        """
        Grafik oluşturulup oluşturulmayacağını belirler.
        
        Args:
            df: Pandas DataFrame
            sql: SQL sorgusu
            
        Returns:
            True ise grafik oluşturulmalı
        """
        # Veri yoksa grafik oluşturma
        if df.empty:
            return False
        
        # Çok fazla satır varsa grafik oluşturma
        if len(df) > 100:
            return False
        
        # Çok az satır varsa grafik oluşturma
        if len(df) < 2:
            return False
        
        # En az 2 sütun olmalı (1 kategori, 1 değer)
        if len(df.columns) < 2:
            return False
        
        # En az 1 sayısal sütun olmalı
        numeric_columns = df.select_dtypes(include=['int64', 'float64', 'int32', 'float32']).columns.tolist()
        if not numeric_columns:
            return False
        
        # SELECT * gibi tüm sütunları getiren sorgularda grafik oluşturma
        if len(df.columns) > 5:
            return False
        
        return True
    
    @staticmethod
    def generate_friendly_error(vn, question: Optional[str], sql: str, error_msg: str) -> str:
        """
        LLM kullanarak kullanıcı dostu bir hata açıklaması oluşturur.
        
        Args:
            vn: Vanna instance (submit_prompt metodunu kullanmak için)
            question: Kullanıcının sorusu (opsiyonel)
            sql: Hatalı SQL sorgusu
            error_msg: Veritabanı hatası mesajı
            
        Returns:
            Türkçe, kullanıcı dostu hata açıklaması
        """
        try:
            # Eğer question yoksa, varsayılan bir mesaj kullan
            question_text = question if question else "SQL sorgusu"
            
            # LLM'e gönderilecek prompt
            prompt_text = (
                f"Kullanıcı şu soruyu sordu: '{question_text}'. "
                f"Oluşturulan SQL: '{sql}'. "
                f"Ancak veritabanı şu hatayı verdi: '{error_msg}'. "
                f"Lütfen bu hatanın nedenini teknik terim kullanmadan, son kullanıcıya hitaben Türkçe olarak kısaca açıkla. "
                f"Örneğin bir sütun yoksa 'Veritabanımızda cinsiyet bilgisi bulunmamaktadır' gibi konuş. "
                f"Sadece açıklamayı döndür, başka bir şey ekleme."
            )
            
            # Vanna'nın submit_prompt metodunu kullan
            prompt = [
                vn.system_message("Sen bir veritabanı hatası açıklama asistanısın. Kullanıcılara teknik olmayan, anlaşılır Türkçe açıklamalar yaparsın."),
                vn.user_message(prompt_text)
            ]
            
            friendly_message = vn.submit_prompt(prompt)
            
            # Eğer LLM yanıt vermezse, varsayılan mesaj döndür
            if not friendly_message or not friendly_message.strip():
                return f"Sorgu çalıştırılırken bir hata oluştu. Lütfen sorgunuzu kontrol edin."
            
            return friendly_message.strip()
            
        except Exception as e:
            # LLM çağrısı başarısız olursa, varsayılan mesaj döndür
            print(f"Warning: Failed to generate friendly error message: {e}")
            return f"Sorgu çalıştırılırken bir hata oluştu: {error_msg[:100]}"
