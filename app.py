from flask import Flask, render_template, request, jsonify, send_from_directory
import os

app = Flask(__name__)

_stt_model = None #lazy loading
_rag_model = None
_tts_model = None

def get_stt():
    global _stt_model
    if _stt_model is None:
        from models.stt import transcribe
        _stt_model = transcribe
    return _stt_model

def get_rag():
    global _rag_model
    if _rag_model is None:
        from models.rag import retrieve
        _rag_model = retrieve
    return _rag_model

def get_tts():
    global _tts_model
    if _tts_model is None:
        from models.tts import speak
        _tts_model = speak
    return _tts_model

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    print("\n" + "="*50)
    print(" Received request")
    print(f"Files: {request.files.keys()}")
    print(f"Form: {request.form.keys()}")
    
    try:
        # Step 1: Get query (text or audio)
        if "audio" in request.files:
            print("Processing audio input...")
            audio = request.files["audio"]
            
            # Save the uploaded file temporarily
            temp_path = "audio/input_temp.webm"
            audio.save(temp_path)
            print(f"Audio saved: {temp_path}")
            
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
                print(f"Converted to WAV: {audio_path}")
            except:
                # Fallback: use pydub
                print("ffmpeg not found, using pydub...")
                from pydub import AudioSegment
                audio_segment = AudioSegment.from_file(temp_path)
                audio_segment = audio_segment.set_frame_rate(16000).set_channels(1)
                audio_segment.export(audio_path, format="wav")
                print(f"Converted to WAV with pydub: {audio_path}")
            
            transcribe = get_stt()
            query = transcribe(audio_path)
            print(f"Transcription: {query}")
        else:
            query = request.form.get("text", "")
            print(f"Text input: {query}")
            if not query:
                print("No input provided")
                return jsonify({"error": "No input provided"}), 400

        # Step 2: Get answer from RAG
        print("Retrieving answer...")
        retrieve = get_rag()
        answer = retrieve(query)
        print(f"Answer: {answer}")
        
        # Step 3: Generate speech
        print("Generating speech...")
        speak = get_tts()
        output_path = "audio/output.wav"
        speak(answer, output_path)
        print(f"Audio generated: {output_path}")

        response = {
            "query": query,
            "answer": answer,
            "audio": "/audio/output.wav"
        }
        print(f"Response: {response}")
        print("="*50 + "\n")
        
        return jsonify(response)
    
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*50 + "\n")
        return jsonify({"error": str(e)}), 500

@app.route("/audio/<filename>")
def serve_audio(filename):
    return send_from_directory("audio", filename)

if __name__ == "__main__":
    os.makedirs("audio", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    
    print("Server starting - models will load on first use")
    app.run(debug=False, host="0.0.0.0", port=5000, use_reloader=False)