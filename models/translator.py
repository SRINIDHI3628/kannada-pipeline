"""
Translator module: Kannada/Hinglish → English
Uses deep-translator for stable, high-quality translation
"""

import re
from deep_translator import GoogleTranslator

# Common Hinglish/Kannada-script keywords for quick mapping
# This helps even if the internet is slow
WORD_MAPPINGS = {
    "vidhava": "widow",
    "vethana": "pension",
    "vetana": "pension",
    "pension": "pension",
    "license": "license",
    "renew": "renewal",
    "madabeku": "need to do",
    "beku": "need",
    "hegidhe": "how is it",
    "yaavaga": "when",
    "certificate": "certificate",
    "marks": "marks",
    "pass": "pass",
    "bus": "bus",
    "freedom": "freedom",
    "fighter": "fighter"
}

def is_kannada(text):
    """Check if text contains Kannada script"""
    kannada_pattern = re.compile(r'[\u0C80-\u0CFF]')
    return bool(kannada_pattern.search(text))

def preprocess_hinglish(text):
    """Simple dictionary-based replacement for Hinglish words"""
    words = text.lower().split()
    translated_words = [WORD_MAPPINGS.get(word, word) for word in words]
    return ' '.join(translated_words)

def translate(text):
    """
    Main translate function used by app.py
    """
    # 1. Handle Hinglish (Latin script Kannada)
    if not is_kannada(text):
        translated = preprocess_hinglish(text)
        print(f"📝 Hinglish normalized: '{text}' → '{translated}'")
        return translated

    # 2. Handle Kannada Script
    try:
        print(f"🔄 Translating Kannada Script: '{text}'")
        translated = GoogleTranslator(source='kn', target='en').translate(text)
        
        # Clean up the output to be safe
        if translated:
            print(f"✅ Translation: '{text}' → '{translated}'")
            return translated
        return text
        
    except Exception as e:
        print(f"❌ Translation Error: {e}")
        # Final fallback: try dictionary mapping
        return preprocess_hinglish(text)
    

def translate_to_kannada(english_text):
    """
    Translates the final LLM response from English back to Kannada.
    This version is optimized for TTS delivery.
    """
    try:
        if not english_text or len(english_text) < 2:
            return ""
            
        print(f"🔄 Translating response to Kannada for TTS...")
        # Translate English -> Kannada
        kannada_output = GoogleTranslator(source='en', target='kn').translate(english_text)
        
        return kannada_output
    except Exception as e:
        print(f"❌ Final Translation Error: {e}")
        return "ಕ್ಷಮಿಸಿ, ಮಾಹಿತಿಯನ್ನು ಅನುವಾದಿಸಲು ಸಾಧ್ಯವಾಗುತ್ತಿಲ್ಲ." # "Sorry, unable to translate info"

if __name__ == "__main__":
    # Quick test
    test_text = "ನನ್ನ ಇಂಕ್ ಸರ್ಟಿಫಿಕೇಟನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಬೇಕು"
    print(f"Result: {translate(test_text)}")