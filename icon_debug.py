from PIL import Image
import os

def check_ico_sizes(file_path):
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    try:
        with Image.open(file_path) as img:
            # .ico files often contain multiple frames (sizes)
            sizes = []
            for i in range(getattr(img, "n_frames", 1)):
                img.seek(i)
                sizes.append(f"{img.size[0]}x{img.size[1]}")
            
            print(f"File: {file_path}")
            print(f"Found {len(sizes)} size layers: {', '.join(sizes)}")
            
            if "16x16" in sizes:
                print("✅ 16x16 found (Required for Title Bar)")
            else:
                print("❌ 16x16 MISSING - Windows will show a generic icon in the title bar.")
                
            if "32x32" in sizes:
                print("✅ 32x32 found (Required for Taskbar)")
            else:
                print("⚠️ 32x32 missing - Windows may stretch other sizes for the taskbar.")
    except Exception as e:
        print(f"Error reading icon: {e}")

if __name__ == "__main__":
    check_ico_sizes("logo.ico")