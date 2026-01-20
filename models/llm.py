"""
LLM module for generating concise, accurate answers
Optimized for low-memory (4-bit quantization and FP16)
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import re
import gc

print("Loading LLM for answer generation...")

# Determine device: CUDA (GPU) is preferred, otherwise CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_NAME = "microsoft/phi-2"

LLM_AVAILABLE = False
tokenizer = None
model = None

try:
    print(f"📥 Loading model: {MODEL_NAME} on {device}")
    
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    
    if device == "cuda":
        # 4-bit Quantization for GPU (Reduces VRAM from 12GB to ~2GB)
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )
    else:
        # Optimization for CPU (Reduces RAM usage by half)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            trust_remote_code=True
        ).to(device)
    
    model.eval()
    print(f"✅ LLM ready on {device}")
    LLM_AVAILABLE = True
    
except Exception as e:
    print(f"⚠️ Primary model failed: {e}")
    print("Trying lighter alternative: TinyLlama...")
    try:
        MODEL_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(
            MODEL_NAME, 
            torch_dtype=torch.float16, 
            device_map="auto"
        )
        LLM_AVAILABLE = True
    except Exception as e2:
        print(f"❌ Critical Error: Could not load any LLM: {e2}")

def extract_relevant_section(document, query, max_length=800):
    """Extracts keyword-relevant sentences to fit in LLM context."""
    query_words = set(re.findall(r'\w+', query.lower()))
    query_words = {w for w in query_words if len(w) > 3}
    
    sentences = re.split(r'[.!?\n]+', document)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    scored_sentences = []
    for i, s in enumerate(sentences):
        score = sum(1 for word in query_words if word in s.lower())
        scored_sentences.append((score, i, s))
    
    scored_sentences.sort(reverse=True, key=lambda x: x[0])
    
    selected = []
    curr_len = 0
    for score, idx, s in scored_sentences:
        if curr_len + len(s) > max_length: break
        selected.append((idx, s))
        curr_len += len(s)
    
    selected.sort(key=lambda x: x[0])
    return ' '.join([s for _, s in selected])

def generate_answer(query, retrieved_document):
    if not LLM_AVAILABLE:
        return "Service information available but LLM engine is offline. Please check manual extraction."

    relevant_info = extract_relevant_section(retrieved_document, query)
    
    # Improved Prompt Engineering for Phi-2
    prompt = f"Instruct: Use the text below to answer the question.\nContext: {relevant_info}\nQuestion: {query}\nOutput:"

    try:
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to(device)
        
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.1, # Lower temperature for factual accuracy
                do_sample=False,
                use_cache=True,
                repetition_penalty=1.2,
                pad_token_id=tokenizer.eos_token_id
            )
        
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Clean up the output to get only the answer
        answer = response.split("Output:")[-1].strip()
        return answer if len(answer) > 10 else "I couldn't find a specific answer in the document."

    except Exception as e:
        print(f"Generation error: {e}")
        return relevant_info[:300]

def format_answer(answer):
    """Basic formatting for UI display."""
    answer = answer.replace(". ", ".\n• ")
    return f"• {answer.strip()}"

if __name__ == "__main__":
    # Quick test case
    test_doc = "Transport Dept: Driving License renewal requires Aadhaar and old license. Fee is 200 INR."
    test_q = "What is the fee for license renewal?"
    print(f"Test Result: {generate_answer(test_q, test_doc)}")