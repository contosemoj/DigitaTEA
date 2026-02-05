import json
import os
import re
import sys

# Ensure output is UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')

def normalize_text(text):
    filename = text.lower()
    filename = filename.replace('á', 'a').replace('à', 'a').replace('ã', 'a').replace('â', 'a')
    filename = filename.replace('é', 'e').replace('ê', 'e')
    filename = filename.replace('í', 'i')
    filename = filename.replace('ó', 'o').replace('õ', 'o').replace('ô', 'o')
    filename = filename.replace('ú', 'u')
    filename = filename.replace('ç', 'c')
    filename = re.sub(r'[^a-z0-9]', '', filename)
    return filename

# Use current directory
cwd = os.getcwd()
game_data_path = os.path.join(cwd, 'gameData.js')
audio_dir = os.path.join(cwd, 'audios')

print(f"Checking in: {cwd}")

if not os.path.exists(audio_dir):
    os.makedirs(audio_dir)

if not os.path.exists(game_data_path):
    print(f"ERROR: gameData.js not found at {game_data_path}")
    sys.exit(1)

with open(game_data_path, 'r', encoding='utf8') as f:
    content = f.read()
    start_idx = content.find('{')
    json_str = content[start_idx:]
    if json_str.strip().endswith(';'):
        json_str = json_str.strip()[:-1]
    
    # Remove trailing commas which are invalid in JSON but valid in JS objects if present
    # This is a naive regex, might need more robustness if JSON is very messy
    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
    
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON Error: {e}")
        # fallback: try using ast.literal_eval if it was a python dict string? No it's JS.
        # Let's hope the regex fixed simple trailing commas.
        sys.exit(1)

required = {} # filename: text

# 1. Levels syllables
levels = data.get('levels', {})
for lvl_id, lvl in levels.items():
    if 'syllables' in lvl:
        for syl in lvl['syllables']:
            fname = normalize_text(syl)
            required[fname] = syl

# 2. Database words and questions
db = data.get('database', {})
for db_id, obj in db.items():
    if 'items' in obj:
        for item in obj['items']:
            # Word
            if 'word' in item:
                fname = normalize_text(item['word'])
                required[fname] = item['word']
            
            # Question Audio
            if 'questionAudio' in item:
                q_fname = item['questionAudio']
                q_text = item.get('question', item.get('word', ''))
                # Remove emojis for TTS text to avoid noise
                q_text_clean = re.sub(r'[^\w\s\?\!\,\.\:\;]', '', q_text)
                required[q_fname] = q_text_clean.strip()

# 3. Hardcoded / System Audios in digita.html
hardcoded = {
    'fimfase': 'Parabéns! Você completou a fase!',
    'erro': 'Erro.',
    'acerto': 'Acerto!',
    'plim': 'Plim',
    'que': 'O que é isso?'
}

existing = set(f.replace('.mp3', '') for f in os.listdir(audio_dir) if f.endswith('.mp3'))

missing = []
for fname, text in required.items():
    if fname not in existing:
        missing.append((fname, text))

print(f"RESUMO DOS ÁUDIOS:")
print(f"------------------")
print(f"Total necessários: {len(required)}")
print(f"Total existentes:  {len(existing)}")
print(f"Total ausentes:    {len(missing)}")

if missing:
    print(f"\nLISTA DE ÁUDIOS AUSENTES ({len(missing)}):")
    for fname, text in missing:
        print(f"- {fname}.mp3 -> Texto: {text}")
else:
    print(f"\nTodos os áudios estão presentes!")

# Write missing to a json file for the generator
if missing:
    with open('missing_audios.json', 'w', encoding='utf8') as f:
        json.dump([{'filename': fname, 'text': text} for fname, text in missing], f, indent=2, ensure_ascii=False)
    print("\nSaved missing audios list to missing_audios.json")
