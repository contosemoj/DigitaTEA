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
# Also check for animal sounds? Usually those are fixed files.
# But if the user says "todos os audios necessarios", I'll stick to speech for now.

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

# List unused if any
unused = []
for f in existing:
    if f not in required and f not in hardcoded:
        unused.append(f)

if unused:
    print(f"\nÁUDIOS QUE PARECEM NÃO ESTAR EM USO ({len(unused)}):")
    for f in unused:
        print(f"- {f}.mp3")
