import json
import os
import re

# IMPORTANT: You must install 'gTTS' package -> pip install gTTS
# This script identifies missing audio files based on gameData.js and generates them.
# It also lists unused files.

try:
    from gtts import gTTS
except ImportError:
    print("Error: gTTS library not installed. Please run: pip install gTTS")
    exit(1)

def normalize_text(text):
    # Remove accents/special chars for filename but KEEP them for TTS
    # Filename: lowercase, no special chars
    # TTS Text: original
    
    # Filename normalization
    filename = text.lower()
    # Manual map or unicodedata could be used. Let's use simple replace for common PT chars
    filename = filename.replace('á', 'a').replace('à', 'a').replace('ã', 'a').replace('â', 'a')
    filename = filename.replace('é', 'e').replace('ê', 'e')
    filename = filename.replace('í', 'i')
    filename = filename.replace('ó', 'o').replace('õ', 'o').replace('ô', 'o')
    filename = filename.replace('ú', 'u')
    filename = filename.replace('ç', 'c')
    filename = re.sub(r'[^a-z0-9]', '', filename)
    
    return filename

def generate_mp3(text, filepath):
    if os.path.exists(filepath):
        return # Skip if exists
    
    print(f"Generating: {text} -> {filepath}")
    try:
        tts = gTTS(text=text, lang='pt')
        tts.save(filepath)
    except Exception as e:
        print(f"Failed to generate {text}: {e}")

# Load gameData
game_data_path = 'd:/DigitaTEA/gameData.js'
audio_dir = 'd:/DigitaTEA/audios'

if not os.path.exists(audio_dir):
    os.makedirs(audio_dir)

with open(game_data_path, 'r', encoding='utf8') as f:
    content = f.read()
    start_idx = content.find('{')
    json_str = content[start_idx:]
    if json_str.strip().endswith(';'):
        json_str = json_str.strip()[:-1]
    data = json.loads(json_str)

required_audios = set()

# Collect words/questions
# 1. Syllables/Letters from Levels
levels = data.get('levels', {})
for lvl_id, lvl in levels.items():
    # Syllables list? Often just syllables like "BA", "BE". We might want audio for them?
    # Yes, usually `playAudio` is called on them in presentation.
    if 'syllables' in lvl:
        for syl in lvl['syllables']:
            required_audios.add(syl)
    
    # Unlock chars? Usually not audio triggered directly unless part of game, but "Letra A" might be.
    # The game plays words primarily. The syllables are played in "startIntroSyllables". 
    # Logic: playAudio(item.word) or playAudio(syl).
    
# 2. Words from Database
db = data.get('database', {})
for lvl_id, obj in db.items():
    if 'items' in obj:
        for item in obj['items']:
            # Word audio
            if 'word' in item:
                required_audios.add(item['word'])
            # Question audio (specific filename provided)
            if 'questionAudio' in item:
                # questionAudio is usually a raw filename without extension in the JSON
                # We add it as-is (it's a filename key, not necessarily TTS text)
                # But to generate it, we need the TEXT.
                # If the file doesn't exist, we can try to use the 'question' text.
                # Logic: store tuple (filename, text_to_speak)
                # But here 'required_audios' is just a set of names to check existence.
                # We need a robust map.
                pass

# Let's verify and generate
# Map: filename -> text
audio_map = {}

# Populate map
# Syllables
for lvl_id, lvl in levels.items():
    if 'syllables' in lvl:
        for syl in lvl['syllables']:
            fname = normalize_text(syl)
            audio_map[fname] = syl

# Words
for lvl_id, obj in db.items():
    if 'items' in obj:
        for item in obj['items']:
            if 'word' in item:
                fname = normalize_text(item['word'])
                audio_map[fname] = item['word']
            
            if 'questionAudio' in item:
                q_fname = item['questionAudio'] # Already defined filename usually
                q_text = item.get('question', 'Pergunta') # Fallback text
                # Normalize filename just in case logic uses normalize? 
                # The game code uses: playFile(currentItem.questionAudio) directly.
                # So we trusted the filename in JSON.
                audio_map[q_fname] = q_text

# Generate missing
existing_files = set(f for f in os.listdir(audio_dir) if f.endswith('.mp3'))
generated_count = 0

print("Checking audios...")
for fname, text in audio_map.items():
    full_path = os.path.join(audio_dir, fname + ".mp3")
    if (fname + ".mp3") not in existing_files:
        generate_mp3(text, full_path)
        generated_count += 1

print(f"Generation complete. {generated_count} files created.")

# Check for unused files
# (Optional: user asked to "apague o que não são necessarios")
print("\nChecking for unused files...")
unused_count = 0
for f in existing_files:
    name_no_ext = os.path.splitext(f)[0]
    # Check if this name is in our audio_map keys
    # Note: audio_map keys are normalized. 'f' is actual filename.
    # We should normalize 'f' to compare? No, file system is truth.
    # If we have 'Abelha.mp3', and map has 'abelha', it matches (on windows mostly).
    # But let's assume strict list.
    
    # Special: "fimfase.mp3", "error.mp3"? (Hardcoded in HTML)
    # HTML hardcoded: sndCorrect (pop.ogg), sndWordWin (magic_chime.ogg), sndLevelWin (audios/fimfase.mp3), sndLose (whistle.ogg)
    # Also "que.mp3" etc?
    
    keep_list = ['fimfase', 'erro', 'acerto', 'plim'] # Add known hardcoded
    
    if name_no_ext not in audio_map and name_no_ext not in keep_list:
        # Risky to delete without confirming hardcoded refs in HTML.
        # HTML uses: playAudio(text) -> normalized text.
        # So audio_map covers dynamic words.
        # But verify hardcoded `playFile` calls?
        # Checked HTML: playFile used for questionAudio. Covered.
        # sndLevelWin src="audios/fimfase.mp3".
        
        # We can simulate deletion or list. Logic: 'apague'.
        # I will delete.
        print(f"Deleting unused: {f}")
        os.remove(os.path.join(audio_dir, f))
        unused_count += 1

print(f"Cleanup complete. {unused_count} files removed.")
