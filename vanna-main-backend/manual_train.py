#!/usr/bin/env python3
"""
Manual training script for testing Semantic Cache
"""
import os
from vanna_config import MyVanna, get_default_config

# Initialize Vanna (same as in main.py)
print("🔧 Initializing Vanna...")
config = get_default_config()
vn = MyVanna(config=config)

# Connect to database
db_path = "/app/db_data/employees.db"
if os.path.exists(db_path):
    vn.connect_to_sqlite(db_path)
    print(f"✅ Connected to database: {db_path}")
else:
    print(f"⚠️  Database not found: {db_path}")

# Manual Training
question = "çalışanların ortalama maaşı nedir?"
sql = "SELECT AVG(salary) as avg_salary FROM employees"

print(f"\n🚀 Training: Question='{question}'")
print(f"   SQL='{sql}'")

try:
    result = vn.train(question=question, sql=sql)
    print(f"✅ Training Successful! Result: {result}")
except Exception as e:
    print(f"❌ Training Failed: {e}")
    import traceback
    traceback.print_exc()

# Test the cache
print("\n🔍 Testing Semantic Cache...")
try:
    if hasattr(vn, 'sql_collection'):
        results = vn.sql_collection.query(
            query_texts=[question],
            n_results=1,
            include=["distances", "documents"]
        )
        print(f"📊 Cache Query Results:")
        print(f"   Distances: {results.get('distances')}")
        print(f"   Documents: {results.get('documents')}")
    else:
        print("⚠️  sql_collection not available")
except Exception as e:
    print(f"❌ Cache Query Failed: {e}")
