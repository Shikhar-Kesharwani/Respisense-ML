import os
import shutil

source_base = r"C:\Users\HP\Downloads\archive (1)\Data"
target_base = r"c:\chest_heart_detection\Artifacts\Data_Ingestion\Chest-CT-Scan-data"

# Remove any existing dummy data
if os.path.exists(target_base):
    shutil.rmtree(target_base)

os.makedirs(os.path.join(target_base, "Adenocarcinoma"), exist_ok=True)
os.makedirs(os.path.join(target_base, "Normal"), exist_ok=True)

splits = ["train", "test", "valid"]

def copy_images(src_folder, target_folder, prefix):
    if not os.path.exists(src_folder):
        return
    for fname in os.listdir(src_folder):
        if fname.endswith(('.png', '.jpg', '.jpeg')):
            src_path = os.path.join(src_folder, fname)
            target_path = os.path.join(target_folder, f"{prefix}_{fname}")
            shutil.copy2(src_path, target_path)

for split in splits:
    # Copy Adenocarcinoma
    adeno_src = os.path.join(source_base, split, "adenocarcinoma_left.lower.lobe_T2_N0_M0_Ib")
    copy_images(adeno_src, os.path.join(target_base, "Adenocarcinoma"), f"{split}_adeno")
    
    # Copy Normal
    normal_src = os.path.join(source_base, split, "normal")
    copy_images(normal_src, os.path.join(target_base, "Normal"), f"{split}_normal")

print("Data successfully copied and prepared!")
