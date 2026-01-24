import os
import re

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

audio_dir = 'd:/DigitaTEA/audios'

if not os.path.exists(audio_dir):
    print("Audio directory not found.")
    exit(1)

files = [f for f in os.listdir(audio_dir) if f.endswith('.mp3')]
rename_count = 0

for f in files:
    name_no_ext = os.path.splitext(f)[0]
    normalized = normalize_text(name_no_ext)
    
    if name_no_ext != normalized:
        old_path = os.path.join(audio_dir, f)
        new_path = os.path.join(audio_dir, normalized + ".mp3")
        
        if os.path.exists(new_path):
            print(f"Skipping {f} -> {normalized}.mp3 (Already exists)")
            # Maybe we should delete the old one?
            # os.remove(old_path)
        else:
            print(f"Renaming: {f} -> {normalized}.mp3")
            os.rename(old_path, new_path)
            rename_count += 1

print(f"Finished renaming {rename_count} files.")
