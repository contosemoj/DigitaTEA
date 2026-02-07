import json
import os
import re

def migrate():
    # Read gameData.js
    with open('f:/DigitaTEA/gameData.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract the JSON part
    # Remove "window.gameData = " and finding the start/end braces properly or just stripping known prefixes
    # The file starts with console.log and then window.gameData = {
    
    match = re.search(r'window\.gameData\s*=\s*({.*});?', content, re.DOTALL)
    if not match:
        # Fallback: try to find the first { and last }
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1:
            json_str = content[start:end+1]
        else:
            print("Could not find JSON object in gameData.js")
            return
    else:
        json_str = match.group(1)

    # Clean up any trailing commas or JS specific quirks if strictly necessary, 
    # but standard json.loads might fail if there are trailing commas.
    # Let's try to load it. If it fails, we might need a more robust parser or regex replacement for trailing commas.
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {e}")
        # Simple attempt to fix trailing commas
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*]', ']', json_str)
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e2:
            print(f"JSON Decode Error after fix attempt: {e2}")
            return

    # Create data directory if not exists
    os.makedirs('f:/DigitaTEA/data', exist_ok=True)

    # 1. Save levels.json (only metadata from levels, not the items/syllables might be needed? 
    # Actually, the original code used 'levels' for the grid and 'database' for the game items.
    # `levels` contained titles, colors, unlocks, syllables (for presentation).
    # `database` contained the items (words, images, emojis).
    
    # We want levels.json to contain the `levels` object so we can render the grid.
    # We want level_X.json to contain the specific data for that level from `database`.
    
    levels = data.get('levels', {})
    database = data.get('database', {})

    # Save levels.json
    with open('f:/DigitaTEA/data/levels.json', 'w', encoding='utf-8') as f:
        json.dump(levels, f, indent=4, ensure_ascii=False)
    print("Created f:/DigitaTEA/data/levels.json")

    # Save individual level data
    # We will save the content of database[id] into level_id.json
    # Note: The original generic code might access database[levelId].
    
    for level_id, level_items in database.items():
        # strict structure: { "items": [...] } usually
        # But let's check what database[level_id] actually is. 
        # Based on index.html: database[currentLevel].items
        
        file_path = f'f:/DigitaTEA/data/level_{level_id}.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(level_items, f, indent=4, ensure_ascii=False)
        print(f"Created {file_path}")

if __name__ == '__main__':
    migrate()
