import json
import os
import re
import sys
import time

try:
    import google.generativeai as genai
except ImportError:
    print("Error: google-generativeai not installed. Please run: pip install -U google-generativeai")
    sys.exit(1)

def strip_emojis(text):
    if not text: return ""
    # Remove emojis and other non-text characters
    # This regex covers a wide range of emojis and special symbols
    return re.sub(r'[^\w\s\?\!\,\.\:\;áàãâéêíóõôúçÁÀÃÂÉÊÍÓÕÔÚÇ]', '', text).strip()

def generate_audio(text, output_path, api_key):
    genai.configure(api_key=api_key)
    
    # Prompt for excited, child-friendly voice
    clean_text = strip_emojis(text)
    prompt = f"Fale de forma MUITO empolgada, amigável e pausada para uma criança: {clean_text}"
    
    print(f"Generating audio for: '{clean_text}' -> {os.path.basename(output_path)}")
    
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
        
        print(f"  Warning: No audio data returned for '{clean_text}'")
        return False

    except Exception as e:
        print(f"  Error generating '{clean_text}': {e}")
        return False

def main():
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Set GOOGLE_API_KEY environment variable.")
        return

    audio_dir = 'f:/DigitaTEA/audios'
    if not os.path.exists(audio_dir):
        os.makedirs(audio_dir)
    
    # Questions for phase 18
    questions = {
        "quemehomemfamilia": "Quem é o Homem da familia? 🤷‍♂️👤 👨 👨‍👩‍👧‍👦❓",
        "quememulherfamilia": "Quem é a mulher da familia? 🤷‍♀️👤 👩 👨‍👩‍👧‍👦❓",
        "quemebebefamilia": "Quem é o bebê da familia? 🤷‍♂️👤 👶 👨‍👩‍👧‍👦❓",
        "quemevovofamilia": "Quem é a vovó da familia? 🤷‍♀️👤 维护 👨‍👩‍👧‍👦❓"
    }
    
    # Wait, I noticed a typo in my manual 'questions' dict for vovó (維護). Correcting.
    questions["quemevovofamilia"] = "Quem é a vovó da familia? 🤷‍♀️👤 👵 👨‍👩‍👧‍👦❓"

    for name, text in questions.items():
        path = os.path.join(audio_dir, name + ".mp3")
        success = generate_audio(text, path, api_key)
        if success:
            print(f"  Successfully synthesized: {name}.mp3")
        else:
            print(f"  Failed: {name}.mp3")
        time.sleep(1) # Avoid rate limits

if __name__ == "__main__":
    main()
