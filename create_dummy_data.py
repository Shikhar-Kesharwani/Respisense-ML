import os
import numpy as np
from PIL import Image

classes = ["Normal", "Adenocarcinoma"]
base_dir = r"c:\chest_heart_detection\Artifacts\Data_Ingestion\Chest-CT-Scan-data"

for cls in classes:
    os.makedirs(os.path.join(base_dir, cls), exist_ok=True)
    for i in range(20): # 20 images per class
        img_array = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        img.save(os.path.join(base_dir, cls, f"{cls}_{i}.png"))

print("Dummy data created successfully!")
