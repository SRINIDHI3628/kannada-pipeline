from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import sys
from models.translator import translate_to_kannada

app = Flask(__name__)

_stt_model = None  # lazy loading
_rag_model = None
_tts_model = None
_translator = None
_llm = None

def get_stt():
    global _stt_model
    if _stt_model is None:
        print("🔧 Loading STT model...")
        from models.stt import transcribe
        _stt_model = transcribe
        print("✅ STT model loaded")
    return _stt_model

def get_translator():
    global _translator
    if _translator is None:
        print("🔧 Loading Translator...")
        from models.translator import translate
        _translator = translate
        print("✅ Translator loaded")
    return _translator

def get_rag():
    global _rag_model
    if _rag_model is None:
        print("🔧 Loading RAG model...")
        from models.rag import retrieve
        _rag_model = retrieve
        print("✅ RAG model loaded")
    return _rag_model

def get_llm():
    global _llm
    if _llm is None:
        print("🔧 Loading LLM...")
        from models.llm import generate_answer, format_answer
        _llm = (generate_answer, format_answer)
        print("✅ LLM loaded")
    return _llm

def get_tts():
    global _tts_model
    if _tts_model is None:
        print("🔧 Loading TTS model...")
        from models.tts import speak
        _tts_model = speak
        print("✅ TTS model loaded")
    return _tts_model

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/health")
def health():
    """Health check endpoint"""
    from pathlib import Path
    
    status = {
        "status": "ok",
        "models": {
            "stt_loaded": _stt_model is not None,
            "rag_loaded": _rag_model is not None,
            "tts_loaded": _tts_model is not None
        },
        "data": {
            "embeddings_exist": Path("processed_data/embeddings.npy").exists(),
            "services_exist": Path("processed_data/services.json").exists(),
            "using_finetuned": Path("processed_data/embeddings.npy").exists() and Path("processed_data/services.json").exists()
        }
    }
    return jsonify(status)

@app.route("/process", methods=["POST"])
def process():
    print("\n" + "="*50)
    print("🎯 Received request")
    print(f"Files: {list(request.files.keys())}")
    print(f"Form: {list(request.form.keys())}")
    
    try:
        # Step 1: Get query (text or audio)
        if "audio" in request.files:
            print("🎤 Processing audio input...")
            audio = request.files["audio"]
            
            # Save the uploaded file temporarily
            temp_path = "audio/input_temp.webm"
            audio.save(temp_path)
            print(f"💾 Audio saved: {temp_path}")
            
            # Convert WebM to WAV
            import subprocess
            audio_path = "audio/input.wav"
            try:
                # Try ffmpeg first
                result = subprocess.run(
                    ['ffmpeg', '-i', temp_path, '-ar', '16000', '-ac', '1', '-y', audio_path],
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    raise Exception("ffmpeg conversion failed")
                print(f"🔄 Converted to WAV: {audio_path}")
            except:
                # Fallback: use pydub
                print("⚠️ ffmpeg not found, using pydub...")
                from pydub import AudioSegment
                audio_segment = AudioSegment.from_file(temp_path)
                audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
                audio_segment.export(audio_path, format="wav")
                print(f"🔄 Converted to WAV with pydub: {audio_path}")
            
            transcribe = get_stt()
            query = transcribe(audio_path)
            print(f"📝 Transcription: {query}")
        else:
            query = request.form.get("text", "")
            print(f"📝 Text input: {query}")
            if not query:
                print("❌ No input provided")
                return jsonify({"error": "No input provided"}), 400

        # Step 2: Translate query to English
        print("🌐 Translating query...")
        translate = get_translator()
        english_query = translate(query)
        print(f"📝 English query: {english_query}")
        
        # Step 3: Retrieve relevant document from RAG
        print("🔍 Retrieving from knowledge base...")
        retrieve = get_rag()
        retrieved_doc = retrieve(english_query)
        print(f"📄 Retrieved document length: {len(retrieved_doc)} chars")
        
        # Step 4: Generate concise answer using LLM
        print("🤖 Generating answer with LLM...")
        generate_answer, format_answer = get_llm()
        raw_answer = generate_answer(english_query, retrieved_doc)
        answer = format_answer(raw_answer)
        print(f"✅ Answer generated: {len(answer)} chars")
        print(f"   Preview: {answer[:100]}...")

        final_kannada_answer = translate_to_kannada(answer)
        
        # Step 5: Generate speech
        print("🔊 Generating speech...")
        speak = get_tts()
        output_path = "audio/output.wav"
        speak(final_kannada_answer, output_path)
        print(f"🎵 Audio generated: {output_path}")

        response = {
            "query": query,
            "answer": final_kannada_answer,
            "audio": "/audio/output.wav"
        }
        print(f"📤 Response: query='{query[:50]}...', answer length={len(answer)}")
        print("="*50 + "\n")
        
        return jsonify(response)
    
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*50 + "\n")
        return jsonify({"error": str(e)}), 500

@app.route("/audio/<filename>")
def serve_audio(filename):
    return send_from_directory("audio", filename)

if __name__ == "__main__":
    # Create required directories
    os.makedirs("audio", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    print("\n" + "="*60)
    print("🚀 KANNADA AI ASSISTANT - STARTING")
    print("="*60)
    
    # Check if fine-tuned data exists
    from pathlib import Path
    if Path("processed_data/embeddings.npy").exists() and Path("processed_data/services.json").exists():
        print("✅ Fine-tuned government services data found!")
        print("   RAG will use fine-tuned MuRIL embeddings")
    else:
        print("⚠️ Fine-tuned data not found - using basic mode")
        print("   Run 'python setup_finetuned_data.py' to enable fine-tuned mode")
    
    print("\n💡 Models will load on first use (lazy loading)")
    print("\n🌐 Server starting at http://localhost:5000")
    print("📊 Health check: http://localhost:5000/health")
    print("="*60 + "\n")
    
    app.run(debug=False, host="0.0.0.0", port=5000, use_reloader=False)