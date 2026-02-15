import json
import os
import re
import sys
import time

# To use this script, install the Google Generative AI library and python-dotenv:
# pip install -U google-generativeai python-dotenv

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass # python-dotenv not installed, will rely on system env vars

try:
    import google.generativeai as genai
    from google.generativeai import protos
except ImportError:
    print("Error: google-generativeai not installed. Please run: pip install -U google-generativeai")
    sys.exit(1)

def normalize_filename(text):
    if not text: return ""
    fn = text.lower()
    fn = fn.replace('á', 'a').replace('à', 'a').replace('ã', 'a').replace('â', 'a')
    fn = fn.replace('é', 'e').replace('ê', 'e')
    fn = fn.replace('í', 'i')
    fn = fn.replace('ó', 'o').replace('õ', 'o').replace('ô', 'o')
    fn = fn.replace('ú', 'u')
    fn = fn.replace('ç', 'c')
    fn = re.sub(r'[^a-z0-9]', '', fn)
    return fn

def get_required_audios(levels_path):
    with open(levels_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    required = {}

    # 1. Levels
    for lvl in data.values():
        if 'syllables' in lvl:
            for syl in lvl['syllables']:
                fn = normalize_filename(syl)
                if fn: required[fn] = syl

    # 2. System (Hardcoded for now as they might not be in levels.json)
    system = {
        'fimfase': 'Parabéns! Você completou a fase!',
        'erro': 'Ops! Tente de novo.',
        'acerto': 'Muito bem!',
        'plim': 'Plim',
        'que': 'O que é isso?'
    }
    for k, v in system.items():
        if k not in required: required[k] = v

    return required

def generate_audio(text, output_path, api_key):
    genai.configure(api_key=api_key)
    
    # We use gemini-1.5-flash which is fastest. 
    # The speech config allows us to specify the Zephyr voice.
    # Note: Prompt engineering helps 'narrating for children'
    prompt = f"Fale de forma muito empolgada, animada e feliz para uma criança: {text}"
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Generation configuration for speech
        # Reference: https://ai.google.dev/gemini-api/docs/text-to-speech
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
        
        # Check if response has audio data
        # In Gemini API, audio is returned as a part with inline_data
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                with open(output_path, 'wb') as f:
                    f.write(part.inline_data.data)
                return True
        
        print(f"  Warning: No audio data returned for '{text}'")
        return False

    except Exception as e:
        print(f"  Error generating '{text}': {e}")
        return False

def main():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Set GOOGLE_API_KEY environment variable.")
        return

    # Set this to True to regenerate ALL audios with the Zephyr voice
    OVERWRITE_EXISTING = True 

    levels_path = 'data/levels.json'
    audio_dir = 'audios'
    
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)

    print(f"Reading levels from {levels_path}...")
    try:
        required = get_required_audios(levels_path)
    except Exception as e:
        print(f"Error reading levels: {e}")
        return

    existing_files = [f.replace('.mp3', '') for f in os.listdir(audio_dir) if f.endswith('.mp3')]
    
    if OVERWRITE_EXISTING:
        to_generate = list(required.items())
        print(f"Full revision requested. Generating ALL {len(to_generate)} audios...")
    else:
        to_generate = [(name, text) for name, text in required.items() if name not in existing_files]
        if not to_generate:
            print("All audios are already present. Set OVERWRITE_EXISTING = True to revise them.")
            return
        print(f"Generating {len(to_generate)} missing audios...")

    # Sort to generate alphabetically/predictably
    to_generate.sort(key=lambda x: x[0])

    for name, text in to_generate:
        path = os.path.join(audio_dir, name + ".mp3")
        
        # Skip if exists and not overwriting
        if not OVERWRITE_EXISTING and os.path.exists(path):
            continue
            
        print(f"Generating {name} ({text})...")
        success = generate_audio(text, path, api_key)
        if success:
            print(f"  Synthesized: {name}.mp3")
        else:
            print(f"  Failed: {name}.mp3")
            
        time.sleep(1) # Avoid rate limits

if __name__ == "__main__":
    main()
