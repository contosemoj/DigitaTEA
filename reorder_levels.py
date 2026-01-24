import json
import collections

# Path to the file
file_path = 'd:/DigitaTEA/gameData.js'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract JSON part
    start_idx = content.find('{')
    if start_idx == -1:
        raise Exception("JSON start not found")
    
    json_str = content[start_idx:]
    # Remove potential trailing semicolon or whitespace if strict
    if json_str.strip().endswith(';'):
        json_str = json_str.strip()[:-1]

    data = json.loads(json_str)
    levels = data['levels']
    db = data['database']

    # We want to move phases 20 and 21 (Presentation) to become 28 and 29.
    # The phases currently at 22-29 should shift down to 20-27.
    
    # 1. Backup Presentation phases
    pres_l20 = levels.get('20')
    pres_l21 = levels.get('21')
    pres_d20 = db.get('20')
    pres_d21 = db.get('21')

    if not pres_l20:
        print("Phase 20 not found, aborting.")
        exit(1)

    # 2. Shift phases 22 to 29 -> 20 to 27
    # Note: We move them one by one. Correct order matters if we were doing in-place without backup, 
    # but here we can just overwrite.
    for i in range(22, 30):
        src = str(i)
        dst = str(i - 2)
        if src in levels:
            levels[dst] = levels[src]
            # Remove old key if it won't be overwritten later?
            # Actually, we are overwriting 20..27. The old 28 and 29 will be overwritten by Presentation.
            # So we don't need to delete explicitly if we cover the range.
        if src in db:
            db[dst] = db[src]

    # 3. Place Presentation at 28 and 29
    levels['28'] = pres_l20
    levels['29'] = pres_l21
    db['28'] = pres_d20
    db['29'] = pres_d21

    # 4. Sort keys cleanly
    new_levels = {k: levels[k] for k in sorted(levels, key=lambda x: int(x))}
    new_db = {k: db[k] for k in sorted(db, key=lambda x: int(x))}

    data['levels'] = new_levels
    data['database'] = new_db

    # Write back
    new_content = "console.log('gameData.js executed');\nwindow.gameData = " + json.dumps(data, indent=4, ensure_ascii=False)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Reorder successful.")

except Exception as e:
    print(f"Error: {e}")
