"""
Setup script to generate fine-tuned embeddings for government services
Run this once to prepare your data for the RAG system
"""

import json
import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from pathlib import Path
import os
from sentence_transformers import SentenceTransformer
import re

# -------- CONFIG --------
RAW_DATA_DIR = Path("raw_data")
PROCESSED_DIR = Path("processed_data")
SERVICES_FILE = PROCESSED_DIR / "services.json"
EMBEDDINGS_FILE = PROCESSED_DIR / "embeddings.npy"
METADATA_FILE = PROCESSED_DIR / "metadata.json"

MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'

# -------- STEP 1: EXTRACT SERVICES FROM RAW TEXT FILES --------
def split_services_from_text(text):
    # Instead of splitting by every double newline, 
    # let's group at least 2-3 paragraphs together.
    blocks = re.split(r'\n\s*\n', text.strip())
    combined_blocks = []
    current_chunk = ""
    
    for b in blocks:
        current_chunk += b + "\n\n"
        if len(current_chunk) > 700: # Aim for a meatier chunk
            combined_blocks.append(current_chunk.strip())
            current_chunk = ""
    if current_chunk:
        combined_blocks.append(current_chunk.strip())
    return combined_blocks

def extract_services():
    """Extract services from all .txt files in raw_data directory"""
    
    if not RAW_DATA_DIR.exists():
        print(f"❌ Error: {RAW_DATA_DIR} directory not found!")
        print(f"📁 Please create it and add your government services .txt files")
        return []
    
    services = []
    service_id = 1
    
    print(f"📂 Scanning {RAW_DATA_DIR} for .txt files...")
    
    for root, dirs, files in os.walk(RAW_DATA_DIR):
        source_page = os.path.basename(root)
        
        for file in files:
            if not file.lower().endswith(".txt"):
                continue
            
            file_path = os.path.join(root, file)
            print(f"   Processing: {file}")
            
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                
                service_blocks = split_services_from_text(content)
                
                for block in service_blocks:
                    first_line = block.split("\n")[0].strip()
                    
                    services.append({
                        "id": service_id,
                        "service_name": first_line,
                        "source_page": source_page,
                        "source_file": file,
                        "text": block
                    })
                    
                    service_id += 1
            
            except Exception as e:
                print(f"   ⚠️ Error processing {file}: {e}")
                continue
    
    return services

# -------- STEP 2: GENERATE EMBEDDINGS USING MuRIL --------
def mean_pooling(model_output, attention_mask):
    """Mean pooling to get sentence embeddings"""
    token_embeddings = model_output.last_hidden_state
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9
    )

# def generate_embeddings(services):
#     """Generate MuRIL embeddings for all services"""
    
#     if not services:
#         print("❌ No services to embed!")
#         return None
    
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     print(f"🔧 Using device: {device}")
    
#     print(f"📥 Loading MuRIL model: {MODEL_NAME}")
#     tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
#     model = AutoModel.from_pretrained(MODEL_NAME).to(device)
#     model.eval()
    
#     texts = [s["text"] for s in services]
#     all_embeddings = []
    
#     print(f"🧮 Generating embeddings for {len(texts)} services...")
    
#     with torch.no_grad():
#         for i, text in enumerate(texts):
#             if (i + 1) % 50 == 0:
#                 print(f"   Progress: {i + 1}/{len(texts)}")
            
#             encoded = tokenizer(
#                 text,
#                 padding=True,
#                 truncation=True,
#                 max_length=512,
#                 return_tensors="pt"
#             )
            
#             encoded = {k: v.to(device) for k, v in encoded.items()}
#             model_output = model(**encoded)
#             embedding = mean_pooling(model_output, encoded["attention_mask"])
#             embedding = embedding.squeeze().cpu().numpy()
            
#             all_embeddings.append(embedding)
    
#     embeddings = np.vstack(all_embeddings)
#     print(f"✅ Embeddings shape: {embeddings.shape}")
    
#     return embeddings


def generate_embeddings(services):
    """Generate high-quality embeddings using SentenceTransformers"""
    
    if not services:
        print("❌ No services to embed!")
        return None
    
    # This replaces all the manual tokenizer/mean_pooling code
    print(f"📥 Loading SMART model: {MODEL_NAME}")
    model = SentenceTransformer(MODEL_NAME)
    
    texts = [s["text"] for s in services]
    
    print(f"🧮 Generating embeddings for {len(texts)} services...")
    
    # This ONE line does everything: tokenizing, processing, and normalizing
    embeddings = model.encode(texts, show_progress_bar=True, normalize_embeddings=True)
    
    print(f"✅ Embeddings shape: {embeddings.shape}")
    return embeddings

# -------- STEP 3: SAVE ALL DATA --------
def save_data(services, embeddings):
    """Save services, embeddings, and metadata"""
    
    # Create processed_data directory
    PROCESSED_DIR.mkdir(exist_ok=True)
    
    # Save services.json
    with open(SERVICES_FILE, "w", encoding="utf-8") as f:
        json.dump(services, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved services to: {SERVICES_FILE}")
    
    # Save embeddings.npy
    np.save(EMBEDDINGS_FILE, embeddings)
    print(f"💾 Saved embeddings to: {EMBEDDINGS_FILE}")
    
    # Save metadata.json (lightweight version for quick reference)
    metadata = [
        {
            "id": s["id"],
            "service_name": s["service_name"],
            "source_page": s["source_page"],
            "source_file": s["source_file"]
        }
        for s in services
    ]
    
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved metadata to: {METADATA_FILE}")

# -------- MAIN EXECUTION --------
def main():
    print("=" * 60)
    print("🚀 FINE-TUNED MODEL SETUP")
    print("=" * 60)
    
    # Step 1: Extract services
    print("\n📋 Step 1: Extracting services from raw data...")
    services = extract_services()
    
    if not services:
        print("\n❌ No services extracted!")
        print("\n💡 Make sure you have:")
        print(f"   1. Created the '{RAW_DATA_DIR}' directory")
        print(f"   2. Added your government services .txt files inside")
        print(f"\n   Example structure:")
        print(f"   {RAW_DATA_DIR}/")
        print(f"   ├── page8/")
        print(f"   │   ├── Revenue Department.txt")
        print(f"   │   └── Public Works Department.txt")
        print(f"   └── page10/")
        print(f"       └── Services.txt")
        return
    
    print(f"\n✅ Extracted {len(services)} services")
    print(f"\n   Sample service names:")
    for s in services[:3]:
        print(f"   - {s['service_name']}")
    
    # Step 2: Generate embeddings
    print("\n🧮 Step 2: Generating MuRIL embeddings...")
    embeddings = generate_embeddings(services)
    
    if embeddings is None:
        return
    
    # Step 3: Save everything
    print("\n💾 Step 3: Saving data...")
    save_data(services, embeddings)
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"   • Total services: {len(services)}")
    print(f"   • Embedding dimensions: {embeddings.shape[1]}")
    print(f"   • Files created:")
    print(f"     - {SERVICES_FILE}")
    print(f"     - {EMBEDDINGS_FILE}")
    print(f"     - {METADATA_FILE}")
    print(f"\n🎯 Your RAG system will now use these fine-tuned embeddings!")
    print(f"   Run your app with: python app.py")

if __name__ == "__main__":
    main()