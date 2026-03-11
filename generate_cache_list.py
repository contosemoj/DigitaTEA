import os
import json

def generate_cache_list():
    base_dir = '.'
    cache_list = []

    # Directories to cache
    dirs_to_cache = ['audios', 'data', 'img']

    for d in dirs_to_cache:
        dir_path = os.path.join(base_dir, d)
        if os.path.exists(dir_path):
            for root, _, files in os.walk(dir_path):
                for f in files:
                    # Ignore python scripts or unnecessary files
                    if not f.endswith('.py') and not f.endswith('.md'):
                        # Create relative URL compatible path (e.g. audios/file.mp3)
                        rel_path = os.path.relpath(os.path.join(root, f), base_dir)
                        # Ensure forward slashes for web URLs
                        web_path = rel_path.replace('\\', '/')
                        # Optionally prepend './' if needed by your SW. Let's stick to standard names.
                        cache_list.push('./' + web_path) if hasattr(cache_list, 'push') else cache_list.append('./' + web_path)

    # Base assets
    cache_list.extend([
        './',
        './index.html',
        './game_icon.png',
        './manifest.json',
        './sw-register.js'
    ])

    # Save to data/cache_list.json
    output_path = os.path.join(base_dir, 'data', 'cache_list.json')
    with open(output_path, 'w', encoding='utf-8') as outfile:
        json.dump(cache_list, outfile, ensure_ascii=False, indent=2)

    print(f"✅ Generated {output_path} with {len(cache_list)} files.")

if __name__ == "__main__":
    generate_cache_list()
