import os
import time
import re

# Try to import GenAI, but don't fail if missing
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# Try to import gTTS
try:
    from gtts import gTTS
    HAS_GTTS = True
except ImportError:
    HAS_GTTS = False
    print("Warning: gTTS not installed. Run 'pip install gTTS'")

def generate_audio_genai(text, output_path, api_key):
    if not HAS_GENAI: return False
    
    genai.configure(api_key=api_key)
    prompt = f"Fale apenas a letra, de forma clara e pausada para uma criança: {text}"
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            prompt,
            generation_config={
                "response_mime_type": "audio/mp3",
                "speech_config": {
                    "voice_config": {
                        "prebuilt_voice_config": {
                            "voice_name": "Zephyr"
                        }
                    }
                }
            }
        )
        
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                with open(output_path, 'wb') as f:
                    f.write(part.inline_data.data)
                return True
        return False
    except Exception as e:
        print(f"GenAI Error: {e}")
        return False

def generate_audio_gtts(text, output_path):
    if not HAS_GTTS: return False
    try:
        tts = gTTS(text=text, lang='pt')
        tts.save(output_path)
        return True
    except Exception as e:
        print(f"gTTS Error: {e}")
        return False

letters = {
    "a": "Á", "b": "Bê", "c": "Cê", "d": "Dê", "e": "Ê", "f": "Efe", "g": "Gê", "h": "Agá",
    "i": "Í", "j": "Jota", "k": "Cá", "l": "Ele", "m": "Eme", "n": "Ene", "o": "Ó", "p": "Pê",
    "q": "Quê", "r": "Erre", "s": "Esse", "t": "Tê", "u": "Ú", "v": "Vê",
    "w": "Dáblio", "x": "Xis", "y": "Ípsilon", "z": "Zê"
}

audio_dir = "audios"
if not os.path.exists(audio_dir):
    os.makedirs(audio_dir)

api_key = os.environ.get("GOOGLE_API_KEY")

for char, pronunciation in letters.items():
    path = os.path.join(audio_dir, f"{char}.mp3")
    
    # Check if exists (optional: force overwrite if needed by user, currently skipping)
    if os.path.exists(path):
         print(f"{char}.mp3 already exists.")
         continue

    print(f"Generating {char} ({pronunciation})...")
    success = False
    
    # Try GenAI first if key exists
    if api_key and HAS_GENAI:
        success = generate_audio_genai(pronunciation, path, api_key)
        if success:
            print(f"  -> Generated with Gemini (Zephyr)")
            time.sleep(1) # Rate limit
    
    # Fallback to gTTS
    if not success and HAS_GTTS:
        print("  -> Fallback to gTTS...")
        success = generate_audio_gtts(pronunciation, path)
        if success:
             print(f"  -> Generated with gTTS")
    
    if not success:
        print(f"  -> Failed to generate {char}.mp3")
