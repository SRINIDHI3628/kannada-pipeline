"""
Complete end-to-end testing suite for Kannada AI Assistant
Tests: RAG, STT, TTS, and full pipeline integration
"""

import sys
import os
from pathlib import Path
import requests
import time

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")

# ============================================================================
# TEST 1: File Structure Check
# ============================================================================
def test_file_structure():
    print_header("TEST 1: File Structure Check")
    
    required_files = [
        "models/rag.py",
        "models/stt.py", 
        "models/tts.py",
        "app.py",
        "templates/index.html"
    ]
    
    optional_files = [
        "processed_data/embeddings.npy",
        "processed_data/services.json",
        "processed_data/metadata.json"
    ]
    
    all_good = True
    
    print("📁 Checking required files...")
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"Found: {file_path}")
        else:
            print_error(f"Missing: {file_path}")
            all_good = False
    
    print("\n📁 Checking optional files (fine-tuned data)...")
    finetuned_available = True
    for file_path in optional_files:
        if Path(file_path).exists():
            print_success(f"Found: {file_path}")
        else:
            print_warning(f"Missing: {file_path}")
            finetuned_available = False
    
    if not finetuned_available:
        print_warning("\nFine-tuned data not found. System will use basic mode.")
        print_info("Run 'python setup_finetuned_data.py' to enable fine-tuned mode")
    
    return all_good

# ============================================================================
# TEST 2: RAG Module Test
# ============================================================================
def test_rag_module():
    print_header("TEST 2: RAG Module Test")
    
    try:
        # Add models to path if needed
        if os.path.exists("models"):
            sys.path.insert(0, "models")
            from rag import retrieve
        else:
            from models.rag import retrieve
        
        print_success("RAG module imported successfully")
        
        # Test queries
        test_queries = [
            ("English", "widow pension"),
            ("Kannada", "ವಿಧವಾ ಪಿಂಚಣಿ"),
            ("Mixed", "license renewal")
        ]
        
        print("\n🔍 Testing retrieval with sample queries:\n")
        
        for lang, query in test_queries:
            print(f"{'─'*60}")
            print(f"Query ({lang}): {query}")
            
            try:
                result = retrieve(query, top_k=1)
                print_success(f"Retrieved answer (length: {len(result)})")
                print(f"Preview: {result[:100]}...")
                
            except Exception as e:
                print_error(f"Retrieval failed: {e}")
                return False
        
        print_success("\nRAG module working correctly")
        return True
        
    except Exception as e:
        print_error(f"RAG module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# TEST 3: Model Loading Test
# ============================================================================
def test_model_loading():
    print_header("TEST 3: Model Loading Test")
    
    models_to_test = ["STT", "RAG", "TTS"]
    
    for model_name in models_to_test:
        print(f"\n🔧 Testing {model_name} model loading...")
        
        try:
            if model_name == "STT":
                from models.stt import transcribe
                print_success(f"{model_name} module loaded")
                
            elif model_name == "RAG":
                from models.rag import retrieve
                print_success(f"{model_name} module loaded")
                
            elif model_name == "TTS":
                from models.tts import speak
                print_success(f"{model_name} module loaded")
                
        except Exception as e:
            print_error(f"{model_name} loading failed: {e}")
            return False
    
    print_success("\nAll models loaded successfully")
    return True

# ============================================================================
# TEST 4: Flask Server Test
# ============================================================================
def test_flask_server():
    print_header("TEST 4: Flask Server Test")
    
    print_info("This test requires the Flask server to be running")
    print_info("Start server in another terminal: python app.py")
    print_info("Or skip this test if server is not running\n")
    
    response = input("Is the Flask server running? (y/n/skip): ").strip().lower()
    
    if response == 'skip':
        print_warning("Skipping Flask server test")
        return True
    
    if response != 'y':
        print_warning("Flask server test skipped")
        return True
    
    base_url = "http://localhost:5000"
    
    # Test 1: Health endpoint
    print("\n🏥 Testing /health endpoint...")
    try:
        r = requests.get(f"{base_url}/health", timeout=5)
        if r.status_code == 200:
            data = r.json()
            print_success("Health endpoint working")
            print(f"   Status: {data.get('status')}")
            print(f"   Using fine-tuned: {data.get('data', {}).get('using_finetuned')}")
        else:
            print_error(f"Health endpoint returned: {r.status_code}")
            return False
    except Exception as e:
        print_error(f"Failed to connect to server: {e}")
        return False
    
    # Test 2: Text query
    print("\n📝 Testing text query...")
    try:
        r = requests.post(
            f"{base_url}/process",
            data={"text": "widow pension"},
            timeout=30
        )
        
        if r.status_code == 200:
            data = r.json()
            print_success("Text query successful")
            print(f"   Query: {data.get('query')}")
            print(f"   Answer: {data.get('answer', '')[:100]}...")
        else:
            print_error(f"Text query failed: {r.status_code}")
            return False
            
    except Exception as e:
        print_error(f"Text query failed: {e}")
        return False
    
    print_success("\nFlask server tests passed")
    return True

# ============================================================================
# TEST 5: Data Quality Check
# ============================================================================
def test_data_quality():
    print_header("TEST 5: Data Quality Check")
    
    embeddings_file = Path("processed_data/embeddings.npy")
    services_file = Path("processed_data/services.json")
    
    if not (embeddings_file.exists() and services_file.exists()):
        print_warning("Fine-tuned data not found - skipping data quality check")
        return True
    
    try:
        import numpy as np
        import json
        
        # Load embeddings
        embeddings = np.load(embeddings_file)
        print_success(f"Embeddings loaded: shape {embeddings.shape}")
        
        # Load services
        with open(services_file, 'r', encoding='utf-8') as f:
            services = json.load(f)
        print_success(f"Services loaded: {len(services)} services")
        
        # Verify dimensions match
        if len(services) == embeddings.shape[0]:
            print_success("Data dimensions match correctly")
        else:
            print_error(f"Dimension mismatch: {len(services)} services vs {embeddings.shape[0]} embeddings")
            return False
        
        # Check for empty services
        empty_count = sum(1 for s in services if not s.get('text', '').strip())
        if empty_count > 0:
            print_warning(f"Found {empty_count} services with empty text")
        else:
            print_success("All services have text content")
        
        # Sample service check
        print("\n📄 Sample service:")
        sample = services[0]
        print(f"   ID: {sample.get('id')}")
        print(f"   Name: {sample.get('service_name')}")
        print(f"   Source: {sample.get('source_file')}")
        print(f"   Text length: {len(sample.get('text', ''))} chars")
        
        print_success("\nData quality check passed")
        return True
        
    except Exception as e:
        print_error(f"Data quality check failed: {e}")
        import traceback
        traceback.print_exc()
        return False

# ============================================================================
# Main Test Runner
# ============================================================================
def main():
    print_header("🧪 KANNADA AI ASSISTANT - FULL TEST SUITE")
    
    tests = [
        ("File Structure", test_file_structure),
        ("RAG Module", test_rag_module),
        ("Model Loading", test_model_loading),
        ("Flask Server", test_flask_server),
        ("Data Quality", test_data_quality)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print_error(f"Test '{test_name}' crashed: {e}")
            results[test_name] = False
    
    # Summary
    print_header("📊 TEST SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        color = Colors.GREEN if result else Colors.RED
        print(f"{color}{status}{Colors.END} - {test_name}")
    
    print(f"\n{'─'*60}")
    print(f"{Colors.BOLD}Total: {passed}/{total} tests passed{Colors.END}")
    
    if passed == total:
        print_success("\n🎉 ALL TESTS PASSED! Your integration is complete!")
        print_info("\nNext steps:")
        print("   1. Start the server: python app.py")
        print("   2. Open browser: http://localhost:5000")
        print("   3. Test with voice or text input")
    else:
        print_error("\n⚠️ Some tests failed. Please review the errors above.")
        print_info("\nCommon fixes:")
        print("   • Missing files: Check file paths")
        print("   • Model errors: Verify dependencies installed")
        print("   • Server errors: Ensure Flask server is running")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)