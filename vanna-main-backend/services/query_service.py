"""
Query Service - Single Responsibility: Saved query operations.
SOLID: Single Responsibility Principle
"""
from typing import List, Optional, Dict, Any
import pandas as pd
import json
from src.db import prisma


class QueryService:
    """Service for handling saved query operations."""
    
    def __init__(self):
        """
        Initialize query service.
        """
        pass
    
    async def save_query(
        self,
        user_id: int,
        question: str,
        sql_query: str,
        is_trained: bool = False
    ) -> Optional[int]:
        """
        Save a user query.
        """
        try:
            saved_query = await prisma.usersavedquery.create(
                data={
                    'user_id': user_id,
                    'question': question,
                    'sql_query': sql_query,
                    'is_trained': is_trained
                }
            )
            return saved_query.id
        except Exception as e:
            print(f"Error saving query: {e}")
            return None
    
    async def get_user_queries(self, user_id: int) -> List[Dict]:
        """
        Get all saved queries for a user.
        """
        queries = await prisma.usersavedquery.find_many(
            where={'user_id': user_id},
            order={'saved_at': 'desc'}
        )
        
        return [
            {
                'id': q.id,
                'question': q.question,
                'sql_query': q.sql_query,
                'saved_at': q.saved_at.isoformat(),
                'is_trained': q.is_trained
            }
            for q in queries
        ]
    
    async def get_query_by_id(self, query_id: int, user_id: int) -> Optional[Dict]:
        """
        Get a specific query by ID (ensuring it belongs to user).
        """
        query = await prisma.usersavedquery.find_first(
            where={
                'id': query_id,
                'user_id': user_id
            }
        )
        
        if query:
            return {
                'id': query.id,
                'question': query.question,
                'sql_query': query.sql_query,
                'saved_at': query.saved_at.isoformat(),
                'is_trained': query.is_trained
            }
        return None
    
    async def delete_query(self, query_id: int, user_id: int) -> bool:
        """
        Delete a query (ensuring it belongs to user).
        """
        try:
            count = await prisma.usersavedquery.delete_many(
                where={
                    'id': query_id,
                    'user_id': user_id
                }
            )
            return count > 0
        except Exception:
            return False
    
    async def mark_as_trained(self, query_id: int, user_id: int) -> bool:
        """
        Mark a query as trained.
        """
        try:
            count = await prisma.usersavedquery.update_many(
                where={
                    'id': query_id,
                    'user_id': user_id
                },
                data={
                    'is_trained': True
                }
            )
            return count > 0
        except Exception:
            return False
    
    @staticmethod
    def check_semantic_cache(vn, question: str, distance_threshold: float = 0.65) -> Optional[str]:
        """
        Check semantic cache for similar questions.
        Uses ChromaDB vector store with proper distance threshold.
        
        Args:
            vn: Vanna instance with vector store
            question: User's question
            distance_threshold: Maximum distance to consider a cache hit (lower = stricter)
                               0.3 = very similar, 0.5 = somewhat similar
            
        Returns:
            Cached SQL string if similar question found, None otherwise
        """
        print(f"\n🔍 [Semantic Cache] Checking cache for question: \"{question[:80]}...\"")
        
        try:
            # Check if vn has sql_collection (ChromaDB_VectorStore)
            if not hasattr(vn, 'sql_collection'):
                print("⚠️  [Semantic Cache] sql_collection not found on Vanna instance")
                return None
            
            # Query ChromaDB with distances to check similarity
            results = vn.sql_collection.query(
                query_texts=[question],
                n_results=1,
                include=["metadatas", "distances", "documents"]
            )
            
            # Safety check: Ensure results structure is valid
            if not results:
                print("📊 [Semantic Cache] No results from ChromaDB")
                print("❌ [Semantic Cache] CACHE MISS - No cached queries")
                return None
            
            distances = results.get('distances')
            documents = results.get('documents')
            
            # Safety checks
            if not distances or len(distances) == 0 or len(distances[0]) == 0:
                print("📊 [Semantic Cache] No similar questions found in cache")
                print("❌ [Semantic Cache] CACHE MISS - No cached queries")
                return None
            
            if not documents or len(documents) == 0 or len(documents[0]) == 0:
                print("⚠️  [Semantic Cache] Documents array is empty")
                return None
            
            distance = distances[0][0]
            doc = documents[0][0]
            
            # Parse the cached document
            try:
                doc_dict = json.loads(doc) if isinstance(doc, str) else doc
                cached_question = doc_dict.get('question', '')
                cached_sql = doc_dict.get('sql', '')
            except (json.JSONDecodeError, TypeError):
                print("⚠️  [Semantic Cache] Failed to parse cached document")
                return None
            
            # Log match details
            print(f"📊 [Semantic Cache] Found potential match:")
            print(f"   🔤 Cached Q: \"{cached_question[:60]}...\"")
            print(f"   📏 Distance: {distance:.4f} (threshold: {distance_threshold})")
            
            # CRITICAL: Check distance threshold to prevent false positives
            if distance > distance_threshold:
                print(f"❌ [Semantic Cache] CACHE MISS - Distance {distance:.4f} > threshold {distance_threshold}")
                print(f"   ℹ️  Questions are not similar enough, falling back to LLM")
                return None
            
            # Distance is within threshold - cache hit!
            if cached_sql:
                print(f"   📝 Cached SQL: {cached_sql[:80]}...")
                print(f"✅ [Semantic Cache] CACHE HIT! Distance {distance:.4f} is below threshold")
                return cached_sql
            else:
                print("⚠️  [Semantic Cache] Match found but SQL is empty")
                return None
                
        except Exception as e:
            print(f"⚠️  [Semantic Cache] Exception occurred: {e}")
            import traceback
            traceback.print_exc()
            return None
        
        return None

    @staticmethod
    def clear_cache(vn) -> dict:
        """
        ChromaDB'deki SQL cache'ini temizler.
        Admin panelinde "Önbelleği Temizle" butonu için kullanılabilir.
        
        Args:
            vn: Vanna instance with vector store
            
        Returns:
            Dict with success status and deleted count
        """
        print("\n🗑️  [Cache Clear] Starting cache clear operation...")
        
        try:
            # Check if vn has sql_collection
            if not hasattr(vn, 'sql_collection'):
                print("⚠️  [Cache Clear] sql_collection not found")
                return {"success": False, "error": "sql_collection not found", "deleted_count": 0}
            
            # Get all items from the collection first to count them
            try:
                all_items = vn.sql_collection.get()
                item_count = len(all_items.get('ids', [])) if all_items else 0
                print(f"📊 [Cache Clear] Found {item_count} items in cache")
            except Exception as e:
                print(f"⚠️  [Cache Clear] Could not count items: {e}")
                item_count = 0
            
            if item_count == 0:
                print("ℹ️  [Cache Clear] Cache is already empty")
                return {"success": True, "message": "Cache already empty", "deleted_count": 0}
            
            # Delete all items from the sql_collection
            # ChromaDB delete requires ids, so we get all and delete
            if all_items and all_items.get('ids'):
                vn.sql_collection.delete(ids=all_items['ids'])
                print(f"✅ [Cache Clear] Successfully deleted {item_count} cached items")
                return {"success": True, "message": f"Deleted {item_count} cached items", "deleted_count": item_count}
            
            return {"success": True, "message": "No items to delete", "deleted_count": 0}
            
        except Exception as e:
            print(f"❌ [Cache Clear] Error: {e}")
            import traceback
            traceback.print_exc()
            return {"success": False, "error": str(e), "deleted_count": 0}

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
    def generate_sql_explanation(question: str, sql: str) -> str:
        """
        SQL sorgusunu analiz ederek kısa Türkçe açıklama oluşturur.
        Backend'de tüm mantık işlemleri burada yapılır.
        """
        sql_upper = sql.upper().strip()
        
        # COUNT sorguları
        if 'COUNT(*)' in sql_upper or 'COUNT(' in sql_upper:
            if 'FROM EMPLOYEES' in sql_upper:
                return 'Toplam çalışan sayısını buluyorum.'
            return 'Kayıt sayısını buluyorum.'
        
        # SELECT sorguları
        if sql_upper.startswith('SELECT'):
            if 'WHERE' in sql_upper:
                return 'Filtrelenmiş verileri getiriyorum.'
            if 'JOIN' in sql_upper:
                return 'Birleştirilmiş verileri getiriyorum.'
            if 'ORDER BY' in sql_upper:
                return 'Sıralanmış verileri getiriyorum.'
            return 'Verileri getiriyorum.'
        
        # Varsayılan açıklama
        return 'SQL sorgusu oluşturuldu.'

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
