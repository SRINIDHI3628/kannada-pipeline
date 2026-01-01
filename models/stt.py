import torch
import soundfile as sf
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

print("Loading STT model...")


device = "cpu"  # Force CPU to save memory

processor = Wav2Vec2Processor.from_pretrained(
    "addy88/wav2vec2-kannada-stt"
)

model = Wav2Vec2ForCTC.from_pretrained( # Memory optimization
    "addy88/wav2vec2-kannada-stt",
    torch_dtype=torch.float32 
).to(device)

model.eval()  
print("STT ready")

def transcribe(audio_path):
    try:
        audio, sr = sf.read(audio_path)
        
        # Resample if needed
        if sr != 16000:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
            sr = 16000

        inputs = processor(
            audio,
            sampling_rate=sr,
            return_tensors="pt",
            padding=True
        )

        with torch.no_grad():
            logits = model(inputs.input_values).logits

        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.decode(predicted_ids[0])
        
        return transcription
    
    except Exception as e:
        print(f"STT error: {e}")
        return "ಕ್ಷಮಿಸಿ, ಧ್ವನಿ ಗುರುತಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ"