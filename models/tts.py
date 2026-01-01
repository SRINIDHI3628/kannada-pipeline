import torch
import soundfile as sf
from transformers import VitsModel, AutoTokenizer

print("Loading TTS model...")

device = "cpu"  # Use CPU to save memory

tokenizer = AutoTokenizer.from_pretrained("facebook/mms-tts-kan")

model = VitsModel.from_pretrained(
    "facebook/mms-tts-kan",
    torch_dtype=torch.float32
    
).to(device)

model.eval()
print("TTS ready")

def speak(text, out_path="audio/output.wav"):
    try:
       
        inputs = tokenizer(text, return_tensors="pt")
        
        if hasattr(inputs, 'input_ids'):
            inputs['input_ids'] = inputs['input_ids'].long()
        
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            output = model(**inputs)
            audio = output.waveform

        audio = audio.cpu().numpy().squeeze()
        
        # Ensure audio is valid
        if len(audio) == 0:
            print("Empty audio generated, creating silence")
            import numpy as np
            audio = np.zeros(16000, dtype=np.float32)
        
        sf.write(out_path, audio, model.config.sampling_rate)
        print(f"TTS audio saved: {out_path}")
        
    except Exception as e:
        print(f"TTS error: {e}")
        # Create silent audio as fallback
        import numpy as np
        silent = np.zeros(16000, dtype=np.float32)
        sf.write(out_path, silent, 16000)
        print(f"Created silent fallback audio")