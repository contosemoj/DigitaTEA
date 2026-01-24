import json

# Data to insert
new_levels = [
    {
        "insert_at": 18,
        "title": "Família",
        "type": "dialogue",
        "introTitle": "Quem é da família?",
        "unlock": [],
        "syllables": ["PAPAI", "MAMÃE", "BEBÊ", "VOVÓ"],
        "color": "bg-blue-50 border-blue-300 text-blue-800",
        "items": [
            {"word": "PAPAI", "emoji": "👨"},
            {"word": "MAMÃE", "emoji": "👩"},
            {"word": "BEBÊ", "emoji": "👶"},
            {"word": "VOVÓ", "emoji": "👵"}
        ]
    },
    {
        "insert_at": 25, 
        "title": "Comida",
        "type": "dialogue",
        "introTitle": "Hora de comer!",
        "unlock": [],
        "syllables": ["BOLO", "BATATA", "BIFE", "OVO"],
        "color": "bg-green-50 border-green-300 text-green-800",
        "items": [
            {"word": "BOLO", "emoji": "🎂"},
            {"word": "BATATA", "emoji": "🥔"},
            {"word": "BIFE", "emoji": "🥩"},
            {"word": "OVO", "emoji": "🥚"}
        ]
    },
    {
        "insert_at": 32,
        "title": "Brincadeiras",
        "type": "dialogue",
        "introTitle": "Vamos brincar?",
        "unlock": [],
        "syllables": ["BOLA", "BONECA", "DADO", "PIPA"],
        "color": "bg-yellow-50 border-yellow-300 text-yellow-800",
        "items": [
           {"word": "BOLA", "emoji": "⚽"},
           {"word": "BONECA", "emoji": "🎎"},
           {"word": "DADO", "emoji": "🎲"},
           {"word": "PIPA", "emoji": "🪁"}
        ]
    }
]

file_path = 'd:/DigitaTEA/gameData.js'

try:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    start_idx = content.find('{')
    json_str = content[start_idx:]
    if json_str.strip().endswith(';'):
        json_str = json_str.strip()[:-1]

    data = json.loads(json_str)
    levels = data['levels']
    db = data['database']

    # Convert keys to int for sorting/manipulation
    # We will rebuild the dictionaries completely
    sorted_level_keys = sorted([int(k) for k in levels.keys()])
    max_level = sorted_level_keys[-1] if sorted_level_keys else -1

    # We need to process insertions. 
    # To avoid index collision during multiple insertions, we can:
    # 1. Convert current state to a list of (id, level, db)
    # 2. Insert new items into list
    # 3. Re-index everything 0..N

    current_list = []
    for k in sorted_level_keys:
        ks = str(k)
        current_list.append({
            'level': levels[ks],
            'db': db.get(ks, {'items': []})
        })

    # Sort new levels by insert_at to handle multiple insertions correctly if needed, 
    # but here we simply assume user provided valid separate indices or we check offsets.
    # Actually, simplest way: Just insert into the Python list at index.
    
    # We must sort new_levels by insert_at descending so we don't mess up earlier indices during valid insertion?
    # No, if we insert into a list, list.insert(index, item) shifts everything right correctly.
    # But if we have multiple insertions:
    # Insert at 18.
    # Insert at 25 (which expects the state AFTER 18 is inserted? or original state?)
    # My manual calculation assumed cumulative state.
    # 18 (Família) -> Original 18 becomes 19.
    # 25 (Comida) -> This index 25 is intended to be after L.
    #    Original L ends at 21. +1 (Família) -> 22. Next is 23.
    #    Wait, my manual calculation in Thinking block said 23. Why did I put 25 in the JSON above?
    #    Let's re-verify.
    #    Original: ... 17(Animais Dialogue) 18(Quiz N) ... 21(L) ... 24(Quiz C) ... 27(S) ...
    #    TARGETS:
    #    Família: After 17. At 18.
    #    Comida: After L (which becomes 22). At 23.
    #    Brincadeiras: After S (which becomes 20+1(L)+1(J)+1(C) ... wait.
    #    Let's use the Python List approach which is safer.
    #    We identify the "ANCHOR" level for each new phase (e.g. "After Level X").
    #    But since titles vary, let's trust the calculated indices if we are careful.
    #    Let's try to stick to "List Insert".
    #    If I insert at 18:
    #       [0..17, NEW, 18(old)...]
    #    Now "Comida". I want it after L.
    #    Find index of L in the NEW list. Insert after it.
    
    # Let's adjust the script logic to find insert positions dynamically based on content if possible, 
    # or just trust the adjusted indices.
    # I will update "new_levels" in the script to simply have the data, and logic below will find where to put them.
    
    to_insert = [
        {"anchor_letter": "M", "offset": 2, "data": new_levels[0]}, # M finishes at 15. Animais at 16,17. Insert at 18.
        {"anchor_letter": "L", "offset": 1, "data": new_levels[1]}, # L finishes at 21 (orig).
        # Wait, anchors are safer.
        {"anchor_letter": "S", "offset": 1, "data": new_levels[2]}  # S finishes at 27 (orig).
    ]
    
    # Re-read list
    working_list = []
    for k in sorted_level_keys:
        ks = str(k)
        working_list.append({
            'level': levels[ks],
            'db': db.get(ks, {'items': []}),
            'debug_title': levels[ks]['title']
        })

    # Helper to find index of LAST level containing a letter unlock or title
    def find_last_index_of_letter(letter, lst):
        last_idx = -1
        for i, obj in enumerate(lst):
            # Check unlocking
            if 'unlock' in obj['level'] and letter in obj['level']['unlock']:
                last_idx = i
            # Check title (fallback)
            elif f"Letra {letter}" in obj['level']['title']:
                last_idx = i
        return last_idx

    # We process insertions. To avoid invalidating indices, we track inserted count or careful search.
    # Better: process insertions one by one, searching in the CURRENT working_list each time.
    
    # 1. Família (After Dialogue Animais or after M? User said "usando apenas letras liberadas". M is last needed.)
    #    Let's put it after 'Sons Animais' (Dialogue) which is usually the last thing before next letter.
    #    Find "Sons Animais" type dialogue.
    
    idx_animais = -1
    for i, obj in enumerate(working_list):
        if "Sons Animais" in obj['level']['title'] and obj['level'].get('type') == 'dialogue':
            idx_animais = i
            break
    
    if idx_animais != -1:
        insert_pos_1 = idx_animais + 1
        # Prepare object
        obj1 = {
            'level': new_levels[0],
            'db': {'items': new_levels[0].pop('items')} # Separate items
        }
        # Clean level data (remove insert_at, items keys if present)
        if 'insert_at' in obj1['level']: del obj1['level']['insert_at']
        
        working_list.insert(insert_pos_1, obj1)
        print(f"Inserted 'Família' at {insert_pos_1}")
    else:
        print("Warning: Could not find anchor for Família")

    # 2. Comida (After L). Find last L.
    idx_l = find_last_index_of_letter('L', working_list)
    if idx_l != -1:
        insert_pos_2 = idx_l + 1
        obj2 = {
            'level': new_levels[1],
            'db': {'items': new_levels[1].pop('items')}
        }
        if 'insert_at' in obj2['level']: del obj2['level']['insert_at']
        working_list.insert(insert_pos_2, obj2)
        print(f"Inserted 'Comida' at {insert_pos_2}")
    else:
         print("Warning: Could not find anchor for Comida")

    # 3. Brincadeiras (After S). Find last S.
    idx_s = find_last_index_of_letter('S', working_list)
    if idx_s != -1:
        insert_pos_3 = idx_s + 1
        obj3 = {
            'level': new_levels[2],
            'db': {'items': new_levels[2].pop('items')}
        }
        if 'insert_at' in obj3['level']: del obj3['level']['insert_at']
        working_list.insert(insert_pos_3, obj3)
        print(f"Inserted 'Brincadeiras' at {insert_pos_3}")
    else:
         print("Warning: Could not find anchor for Brincadeiras")


    # Rebuild Dictionary
    final_levels = {}
    final_db = {}
    
    for i, obj in enumerate(working_list):
        ks = str(i)
        final_levels[ks] = obj['level']
        final_db[ks] = obj['db']

    data['levels'] = final_levels
    data['database'] = final_db

    new_content = "console.log('gameData.js executed');\nwindow.gameData = " + json.dumps(data, indent=4, ensure_ascii=False)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("Insertion successful.")

except Exception as e:
    print(f"Error: {e}")
