import json
import re
import sys

# Set encoding to utf-8 for stdout explicitly to avoid potential charmap errors on Windows
sys.stdout.reconfigure(encoding='utf-8')

file_path = "d:/DigitaTEA/gameData.js"

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
except FileNotFoundError:
    print(f"Error: File not found at {file_path}")
    sys.exit(1)

# Extract JSON part.
start_marker = "window.gameData ="
start_index = content.find(start_marker)
if start_index == -1:
    print("Error: Could not find start of object 'window.gameData ='")
    sys.exit(1)

json_str = content[start_index + len(start_marker):].strip()
if json_str.endswith(';'):
    json_str = json_str[:-1]

try:
    # Attempt to clean potential trailing commas if any (regex: Replace ,} with } and ,] with ])
    # Though standard JSON doesn't allow them, our generator might be clean.
    json_str = re.sub(r',\s*([\]}])', r'\1', json_str)
    data = json.loads(json_str) 
except json.JSONDecodeError as e:
    print(f"JSON Error: {e}")
    sys.exit(1)

levels = data.get('levels', {})
database = data.get('database', {})

new_levels = {}
new_database = {}

# Sort keys numerically
try:
    keys = sorted([int(k) for k in levels.keys()])
except ValueError:
    print("Error: Non-numeric keys found in levels.")
    # Fallback to string sort if fails
    keys = sorted(levels.keys())

new_id_counter = 0

for old_id in keys:
    str_id = str(old_id)
    lvl = levels[str_id]
    db_item = database.get(str_id, {"items": []})
    
    # Check type
    lvl_type = lvl.get('type', 'syllables').lower()
    
    # Logic: If ALREADY a quiz, keep it. If NOT a quiz, add a Quiz version BEFORE it.
    if lvl_type == 'quiz':
        # Just copy
        new_levels[str(new_id_counter)] = lvl
        new_database[str(new_id_counter)] = db_item
        new_id_counter += 1
    else:
        # Create Pre-Quiz Level
        quiz_lvl = lvl.copy()
        quiz_lvl['title'] = "Quiz: " + lvl['title']
        quiz_lvl['type'] = 'quiz'
        
        # Don't unlock the official letter reward in the quiz warm-up
        quiz_lvl['unlock'] = [] 
        
        # Optional: Change color slightly? No, keeping consistent is improved for association.
        
        new_levels[str(new_id_counter)] = quiz_lvl
        new_database[str(new_id_counter)] = db_item 
        new_id_counter += 1
        
        # Then Original Level
        new_levels[str(new_id_counter)] = lvl
        new_database[str(new_id_counter)] = db_item
        new_id_counter += 1

new_data = {
    "levels": new_levels,
    "database": new_database
}

# Output JS
js_content = "console.log('gameData.js executed');\nwindow.gameData = " + json.dumps(new_data, indent=4, ensure_ascii=False) + ";"

try:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"Success: Processed {len(keys)} original levels into {len(new_levels)} levels.")
except Exception as e:
    print(f"Error writing file: {e}")
