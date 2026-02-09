import json

# Original file path
file_path = r'f:\DigitaTEA\data\ZHKRxjwKnXM.json'

# New data provided by user
new_timestamps = [
  {
    "text": "VENTO VENTANIA ME LEVE PARA AS BORDAS DO CÉU",
    "start": 19.4,
    "end": 24.8
  },
  {
    "text": "EU VOU PUXAR AS BARBAS DE DEUS",
    "start": 24.8,
    "end": 33.1
  },
  {
    "text": "VENTO VENTANIA ME LEVE PRA ONDE NASCE A CHUVA",
    "start": 33.1,
    "end": 40
  },
  {
    "text": "PRA LÁ DE ONDE O VENTO FAZ A CURVA",
    "start": 40,
    "end": 46.9
  },
  {
    "text": "ME DEIXE CAVALGAR NOS SEUS DESATINOS",
    "start": 46.9,
    "end": 50.6
  },
  {
    "text": "NAS REVOADAS REDEMOINHOS",
    "start": 50.6,
    "end": 55.3
  },
  {
    "text": "VENTO VENTANIA ME LEVE SEM DESTINO",
    "start": 55.3,
    "end": 62.2
  },
  {
    "text": "QUERO JUNTAR ME A VOCÊ",
    "start": 62.2,
    "end": 66.2
  },
  {
    "text": "E CARREGAR OS BALÕES PRO MAR",
    "start": 66.2,
    "end": 69.2
  },
  {
    "text": "QUERO ENROLAR AS PIPAS NOS FIOS",
    "start": 69.2,
    "end": 73
  },
  {
    "text": "MANDAR MEUS BEIJOS PELO AR",
    "start": 73,
    "end": 76.6
  },
  {
    "text": "VENTO VENTANIA ME LEVE PRA QUALQUER LUGAR",
    "start": 76.6,
    "end": 82.5
  },
  {
    "text": "ME LEVE PARA QUALQUER CANTO DO MUNDO",
    "start": 82.5,
    "end": 86.1
  },
  {
    "text": "ÁSIA EUROPA AMÉRICA",
    "start": 86.1,
    "end": 106
  },
  {
    "text": "VENTO VENTANIA ME LEVE PARA AS BORDAS DO CÉU",
    "start": 106,
    "end": 114.2
  },
  {
    "text": "EU VOU PUXAR AS BARBAS DE DEUS",
    "start": 114.2,
    "end": 119.6
  },
  {
    "text": "ME LEVE PARA ONDE NASCE A CHUVA",
    "start": 119.6,
    "end": 125.4
  },
  {
    "text": "VENTO VENTANIA ME LEVE PARA OS QUATRO CANTOS DO MUNDO",
    "start": 125.4,
    "end": 134.4
  },
  {
    "text": "ME LEVE PRA QUALQUER LUGAR",
    "start": 134.4,
    "end": 136.9
  },
  {
    "text": "PRA LÁ DE ONDE O VENTO FAZ A CURVA",
    "start": 136.9,
    "end": 142.9
  },
  {
    "text": "ME DEIXE CAVALGAR NOS SEUS DESATINOS",
    "start": 142.9,
    "end": 148.1
  },
  {
    "text": "NAS REVOADAS REDEMOINHOS",
    "start": 148.1,
    "end": 154.9
  },
  {
    "text": "VENTO VENTANIA ME LEVE SEM DESTINO",
    "start": 154.9,
    "end": 164.1
  },
  {
    "text": "QUERO MOVER AS PÁS DOS MOINHOS",
    "start": 164.1,
    "end": 169
  },
  {
    "text": "E ABRANDAR O CALOR DO SOL",
    "start": 169,
    "end": 173.1
  },
  {
    "text": "QUERO EMARANHAR O CABELO DA MENINA",
    "start": 173.1,
    "end": 178
  },
  {
    "text": "MANDAR MEUS BEIJOS PELO AR",
    "start": 178,
    "end": 183
  },
  {
    "text": "VENTO VENTANIA AGORA QUE EU ESTOU SOLTO NA VIDA",
    "start": 183,
    "end": 191.3
  },
  {
    "text": "ME LEVE PRA QUALQUER LUGAR",
    "start": 191.3,
    "end": 195.9
  },
  {
    "text": "ME LEVE MAS NÃO ME FAÇA VOLTAR",
    "start": 195.9,
    "end": 201.2
  },
  {
    "text": "LÊ LÊ LÊ LÊ",
    "start": 201.2,
    "end": 203.5
  },
  {
    "text": "LÊ LÊ LÊ LÊ",
    "start": 203.5,
    "end": 206
  },
  {
    "text": "LÊ LÊ LÊ LÊ LÊ LÊ LÊ LÊ",
    "start": 206,
    "end": 211
  }
]

# Load existing data
try:
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    current_subtitles = data['timedSubtitles']
    
    # Merge
    print(f"Merging {len(new_timestamps)} new timestamps into {len(current_subtitles)} existing subtitles...")
    
    # Use index-based merging since the text order is preserved
    for i, new_sub in enumerate(new_timestamps):
        if i < len(current_subtitles):
            current_subtitles[i]['start'] = new_sub['start']
            current_subtitles[i]['end'] = new_sub['end']
            # Optional: normalize text if needed, but we trust the existing file usually
            # But let's check if there's a mismatch just in case
            # normalized_old = current_subtitles[i]['text'].strip().upper()
            # normalized_new = new_sub['text'].strip().upper()
            # if normalized_old != normalized_new:
            #     print(f"Warning: Text mismatch at index {i}. Old: '{normalized_old}' New: '{normalized_new}'")
        else:
            print(f"Warning: New timestamp index {i} exceeds existing subtitles count.")
            
    # Save back
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print("Successfully updated subtitles.")

except Exception as e:
    print(f"Error: {e}")
