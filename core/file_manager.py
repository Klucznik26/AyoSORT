import os
import shutil

def scan_images(folder, extensions):
    return [f for f in os.listdir(folder) if os.path.splitext(f)[1].lower() in extensions]

def create_directories(base_path, subdirs):
    for subdir in subdirs:
        os.makedirs(os.path.join(base_path, subdir), exist_ok=True)

def copy_image(src_path, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    shutil.copy2(src_path, dest_path)