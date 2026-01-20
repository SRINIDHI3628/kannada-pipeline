import os
import numpy as np
import torch
import faiss
import json
from pathlib import Path
from transformers import AutoTokenizer, AutoModel
from sentence_transformers import SentenceTransformer

print("Loading RAG model...")

device = "cpu"

# Use MuRIL for multilingual embeddings
model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'

model = SentenceTransformer(model_name, device="cpu")

# Paths for fine-tuned model data
EMBEDDINGS_FILE = Path("processed_data/embeddings.npy")
SERVICES_FILE = Path("processed_data/services.json")
DOCS_FILE = Path("data/docs.txt")

def mean_pooling(model_output, attention_mask):
    """Mean pooling to get sentence embeddings"""
    token_embeddings = model_output.last_hidden_state
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9
    )

# def embed(text):
#     """Generate embeddings for text using MuRIL"""
#     encoded_input = tokenizer(
#         text, 
#         padding=True, 
#         truncation=True, 
#         max_length=512,
#         return_tensors='pt'
#     ).to(device)
    
#     with torch.no_grad():
#         model_output = model(**encoded_input)
    
#     embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
    
#     # Normalize embeddings
#     embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
    
#     return embeddings[0].cpu().numpy()

def embed(text):
    """Generate high-quality embeddings using SentenceTransformers"""
    # This automatically handles tokenization, pooling, and normalization
    return model.encode(text, normalize_embeddings=True)

# Check if fine-tuned embeddings exist
use_finetuned = False
docs = []
doc_embeddings = None
index = None

if EMBEDDINGS_FILE.exists() and SERVICES_FILE.exists():
    print("🎯 Loading fine-tuned government services model...")
    
    # Load pre-computed embeddings
    doc_embeddings = np.load(EMBEDDINGS_FILE).astype("float32")
    
    # Load services data
    with open(SERVICES_FILE, "r", encoding="utf-8") as f:
        services_data = json.load(f)
    
    # Extract text for retrieval
    docs = [s["text"] for s in services_data]
    
    # Create FAISS index with L2 distance
    dim = doc_embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(doc_embeddings)
    
    use_finetuned = True
    print(f"✅ Loaded {len(docs)} government services with fine-tuned embeddings")
    
else:
    print("⚠️ Fine-tuned model not found, using basic docs...")
    
    # Fallback to basic docs.txt
    if not DOCS_FILE.exists():
        print(f"Warning: {DOCS_FILE} not found, creating sample...")
        os.makedirs("data", exist_ok=True)
        with open(DOCS_FILE, "w", encoding="utf-8") as f:
            f.write("ನಮಸ್ಕಾರ! ನಾನು ಕನ್ನಡ AI ಸಹಾಯಕ.\n")
            f.write("Hello! I am a Kannada AI assistant.\n")
            f.write("ಬೆಂಗಳೂರು ಕರ್ನಾಟಕದ ರಾಜಧಾನಿ.\n")
            f.write("Bangalore is the capital of Karnataka.\n")
    
    docs = open(DOCS_FILE, encoding="utf-8").read().splitlines()
    docs = [d.strip() for d in docs if d.strip()]
    
    if not docs:
        docs = ["ಕ್ಷಮಿಸಿ, ಯಾವುದೇ ಡೇಟಾ ಲಭ್ಯವಿಲ್ಲ. Sorry, no data available."]
    
    print(f"Loaded {len(docs)} basic documents")
    print(f"Generating embeddings...")
    
    # Generate embeddings for basic docs
    doc_embeddings_list = []
    for i, doc in enumerate(docs):
        if i % 10 == 0:
            print(f"   Processing {i}/{len(docs)}...")
        emb = embed(doc)
        doc_embeddings_list.append(emb)
    
    doc_embeddings = np.vstack(doc_embeddings_list).astype("float32")
    
    # Create FAISS index
    dim = doc_embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(doc_embeddings)

print(f"RAG ready with {len(docs)} documents (Fine-tuned: {use_finetuned})")

def retrieve(query, top_k=1):
    """Retrieve most relevant document for query"""
    try:
        # Generate query embedding
        q_emb = embed(query).astype("float32").reshape(1, -1)
        
        # Search for most similar documents
        distances, indices = index.search(q_emb, top_k)
        
        # Get best match
        best_idx = indices[0][0]
        best_distance = distances[0][0]
        best_match = docs[best_idx]
        
        print(f"Query: '{query}'")
        print(f"Distance: {best_distance:.4f}")
        print(f"Best match: {best_match[:100]}...")
        
        return best_match
        
    except Exception as e:
        print(f"RAG error: {e}")
        import traceback
        traceback.print_exc()
        return "ಕ್ಷಮಿಸಿ, ನಾನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲಿಲ್ಲ. Sorry, I didn't understand."