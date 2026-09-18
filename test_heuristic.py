import os
from PIL import Image, ImageStat
import numpy as np
import glob

def check_image(path):
    try:
        img = Image.open(path).convert('RGB')
    except Exception as e:
        return f"Error opening image: {e}"
    
    # 1. Check if Grayscale (variance across color channels is near 0)
    # We can check color variance by taking standard deviation of colors
    stat = ImageStat.Stat(img)
    # stat.var returns [var_R, var_G, var_B]
    # To check if it's grayscale, we can check the difference between R, G, B channels per pixel
    img_arr = np.array(img, dtype=np.int16)
    r = img_arr[:, :, 0]
    g = img_arr[:, :, 1]
    b = img_arr[:, :, 2]
    
    color_diff_var = np.var(r - g) + np.var(r - b) + np.var(g - b)
    
    # 2. Check histogram (CT scans have lots of black)
    gray = img.convert('L')
    gray_arr = np.array(gray)
    dark_pixels = np.sum(gray_arr < 20) / (gray_arr.shape[0] * gray_arr.shape[1])
    
    return f"Color Variance: {color_diff_var:.2f}, Dark Pixels: {dark_pixels:.2%}"

print("Checking a real CT Scan:")
sample_ct = os.path.join("Artifacts", "Data_Ingestion", "Chest-CT-Scan-data", "Normal", "test_normal_10.png")
if os.path.exists(sample_ct):
    print(check_image(sample_ct))
else:
    print(f"Sample scan not found at {sample_ct}")

print("\nChecking the dummy internet scan (if it exists):")
print(check_image("test_internet_scan.png"))
