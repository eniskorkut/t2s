import logging
import sys
from vanna_config import MyVanna, get_default_config

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

def test_semantic_similarity():
    print("\n🧪 Testing Semantic Similarity with Multilingual Model")
    print("==================================================")
    
    # Initialize Vanna
    try:
        config = get_default_config()
        vn = MyVanna(config=config)
        print("✅ Vanna initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Vanna: {e}")
        return

    # Define test queries
    # These are semantically identical but phrased differently in Turkish
    query1 = "en yüksek maaşla çalışan kim?"
    query2 = "en yüksek maaş alan kim?"
    
    print(f"\n📝 Query 1: '{query1}'")
    print(f"📝 Query 2: '{query2}'")
    
    # Manually calculate embedding distance using ChromaDB collection
    # We clear the collection first to have a clean slate
    print("\n🧹 Clearing collection for test...")
    if hasattr(vn, 'sql_collection'):
        try:
            ids = vn.sql_collection.get()['ids']
            if ids:
                vn.sql_collection.delete(ids=ids)
        except Exception as e:
            print(f"Warning clearing collection: {e}")
            
    # Train with Q1
    print(f"🎓 Training with Query 1...")
    sql = "SELECT * FROM employees ORDER BY salary DESC LIMIT 1"
    vn.train(question=query1, sql=sql)
    
    # Query with Q2
    print(f"🔍 Searching with Query 2...")
    results = vn.sql_collection.query(
        query_texts=[query2],
        n_results=1,
        include=["distances", "documents", "metadatas"]
    )
    
    distances = results.get('distances', [[]])[0]
    documents = results.get('documents', [[]])[0]
    
    if not distances:
        print("❌ No results found!")
        return
        
    distance = distances[0]
    print(f"\n📊 RESULTS:")
    print(f"   Distance: {distance:.4f}")
    
    # Evaluation
    # With multilingual model, distance should be much lower (e.g., < 0.4)
    # With default model, it was ~1.4
    if distance < 0.4:
        print("✅ SUCCESS: Distance is low (< 0.4). Semantic match detected!")
    elif distance < 0.6:
        print("⚠️  PARTIAL SUCCESS: Distance is better but still high (< 0.6).")
    else:
        print("❌ FAILURE: Distance is essentially the same as before (> 0.6). Model might not be loaded.")

if __name__ == "__main__":
    test_semantic_similarity()
