import os
import numpy as np
import torch
import faiss
from transformers import AutoTokenizer, AutoModel

print("Loading RAG model...")

device = "cpu"

# Use XLM-RoBERTa for multilingual embeddings
# model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
model_name = "google/muril-base-cased"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name).to(device)
model.eval()

def mean_pooling(model_output, attention_mask):
    """Mean pooling to get sentence embeddings"""
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

def embed(text):
    """Generate embeddings for text"""
    encoded_input = tokenizer(
        text, 
        padding=True, 
        truncation=True, 
        max_length=128,
        return_tensors='pt'
    ).to(device)
    
    with torch.no_grad():
        model_output = model(**encoded_input)
    
    embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
    
    # Normalize embeddings
    embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
    
    return embeddings[0].cpu().numpy()

# Load knowledge base
docs_path = "data/docs.txt"
if not os.path.exists(docs_path):
    print(f"Warning: {docs_path} not found, creating sample...")
    os.makedirs("data", exist_ok=True)
    with open(docs_path, "w", encoding="utf-8") as f:
        f.write("ನಮಸ್ಕಾರ! ನಾನು ಕನ್ನಡ AI ಸಹಾಯಕ.\n")
        f.write("Hello! I am a Kannada AI assistant.\n")
        f.write("ಬೆಂಗಳೂರು ಕರ್ನಾಟಕದ ರಾಜಧಾನಿ.\n")
        f.write("Bangalore is the capital of Karnataka.\n")

docs = open(docs_path, encoding="utf-8").read().splitlines()
docs = [d.strip() for d in docs if d.strip()]  # Remove empty lines

if not docs:
    docs = ["ಕ್ಷಮಿಸಿ, ಯಾವುದೇ ಡೇಟಾ ಲಭ್ಯವಿಲ್ಲ. Sorry, no data available."]

print(f"Loaded {len(docs)} documents")
print(f"Generating embeddings...")

# Generate embeddings for all documents
doc_embeddings = []
for i, doc in enumerate(docs):
    if i % 10 == 0:
        print(f"   Processing {i}/{len(docs)}...")
    emb = embed(doc)
    doc_embeddings.append(emb)

doc_embeddings = np.vstack(doc_embeddings).astype("float32")

# Create FAISS index (using inner product since embeddings are normalized)
index = faiss.IndexFlatIP(doc_embeddings.shape[1])
index.add(doc_embeddings)

print(f"RAG ready with {len(docs)} documents")

def retrieve(query, top_k=1):
    """Retrieve most relevant document for query"""
    try:
        # Generate query embedding
        q_emb = embed(query).astype("float32").reshape(1, -1)
        
        # Search for most similar documents
        scores, indices = index.search(q_emb, top_k)
        
        # Get best match
        best_idx = indices[0][0]
        best_score = scores[0][0]
        best_match = docs[best_idx]
        
        print(f"Query: '{query}'")
        print(f"Similarity score: {best_score:.4f}")
        print(f"Best match: {best_match[:100]}...")
        
        return best_match
        
    except Exception as e:
        print(f"RAG error: {e}")
        import traceback
        traceback.print_exc()
        return "ಕ್ಷಮಿಸಿ, ನಾನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲಿಲ್ಲ. Sorry, I didn't understand."