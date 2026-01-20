"""
Test script to verify the fine-tuned RAG integration
Run this after setup_finetuned_data.py to test retrieval
"""

import sys
from pathlib import Path

# Check if processed data exists
PROCESSED_DIR = Path("processed_data")
EMBEDDINGS_FILE = PROCESSED_DIR / "embeddings.npy"
SERVICES_FILE = PROCESSED_DIR / "services.json"

print("=" * 60)
print("🧪 TESTING FINE-TUNED RAG INTEGRATION")
print("=" * 60)

# Step 1: Check files
print("\n📁 Step 1: Checking required files...")

if not EMBEDDINGS_FILE.exists():
    print(f"❌ Missing: {EMBEDDINGS_FILE}")
    print(f"\n💡 Run this first: python setup_finetuned_data.py")
    sys.exit(1)

if not SERVICES_FILE.exists():
    print(f"❌ Missing: {SERVICES_FILE}")
    print(f"\n💡 Run this first: python setup_finetuned_data.py")
    sys.exit(1)

print(f"✅ Found: {EMBEDDINGS_FILE}")
print(f"✅ Found: {SERVICES_FILE}")

# Step 2: Load RAG module
print("\n🔧 Step 2: Loading RAG module...")

try:
    # Add models directory to path if needed
    import os
    if os.path.exists("models"):
        sys.path.insert(0, "models")
        from rag import retrieve
    else:
        from models.rag import retrieve
    
    print("✅ RAG module loaded successfully")
except Exception as e:
    print(f"❌ Error loading RAG: {e}")
    print("\n💡 Make sure your updated rag.py is in the models/ directory")
    sys.exit(1)

# Step 3: Test queries
print("\n🔍 Step 3: Testing retrieval...")

test_queries = [
    "widow pension",
    "ವಿಧವಾ ಪಿಂಚಣಿ",
    "driving license renewal",
    "bus pass",
    "freedom fighter pension",
    "marks certificate"
]

print(f"\nTesting {len(test_queries)} sample queries:\n")

for i, query in enumerate(test_queries, 1):
    print(f"\n{'─' * 60}")
    print(f"Query {i}: {query}")
    print(f"{'─' * 60}")
    
    try:
        result = retrieve(query)
        print(f"\n📄 Retrieved Answer:")
        print(f"{result[:200]}..." if len(result) > 200 else result)
    except Exception as e:
        print(f"❌ Error: {e}")

# Step 4: Interactive mode
print(f"\n\n{'=' * 60}")
print("✅ BASIC TESTS COMPLETE!")
print("=" * 60)

print("\n🎯 Interactive Mode - Test your own queries")
print("Type 'exit' to quit\n")

while True:
    try:
        user_query = input("Enter your question: ").strip()
        
        if user_query.lower() == 'exit':
            print("\n👋 Goodbye!")
            break
        
        if not user_query:
            continue
        
        print(f"\n🔍 Searching for: {user_query}")
        result = retrieve(user_query)
        
        print(f"\n📄 Answer:")
        print(f"{result}\n")
        print(f"{'─' * 60}\n")
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        break
    except Exception as e:
        print(f"❌ Error: {e}\n")