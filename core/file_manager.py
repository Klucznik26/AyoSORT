import os
import shutil

def create_directories(base_path, subdirs):
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    for subdir in subdirs:
        path = os.path.join(base_path, subdir)
        if not os.path.exists(path):
            os.makedirs(path)

def copy_image(src_path, dest_path):
    try:
        shutil.copy2(src_path, dest_path)
        return True
    except Exception as e:
        raise e