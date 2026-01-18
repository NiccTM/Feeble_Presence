from PIL import Image
import os

def fix_my_icon(input_path, output_path="logo_fixed.ico"):
    try:
        img = Image.open(input_path)
        # Standard Windows Icon sizes
        sizes = [(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
        
        # Save with all layers
        img.save(output_path, sizes=sizes)
        print(f"✅ Success! Generated {output_path} with all required layers.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fix_my_icon("logo.ico")