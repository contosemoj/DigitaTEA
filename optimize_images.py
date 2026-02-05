import os
from PIL import Image

def optimize_images(directory="img", max_size=(512, 512)):
    if not os.path.exists(directory):
        print(f"Directory {directory} not found.")
        return

    for filename in os.listdir(directory):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(directory, filename)
            try:
                with Image.open(filepath) as img:
                    # Calculate new size maintaining aspect ratio
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Save optimized image
                    img.save(filepath, optimize=True, quality=85)
                    print(f"Optimized: {filename}")
            except Exception as e:
                print(f"Failed to optimize {filename}: {e}")

if __name__ == "__main__":
    optimize_images()
