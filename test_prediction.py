import os
import shutil
import json
import random
from Respire.Pipeline.Prediction_Pipeline import PredictionPipeline

# The web scraping from Wikipedia/GitHub kept throwing 403/404 security blocks.
# To test on an unseen "proper CT scan", we pull a random image from the untouched 'test' split.
test_dir = r"C:\Users\HP\Downloads\archive (1)\Data\test\normal"
images = os.listdir(test_dir)
random_image = random.choice(images)
source_path = os.path.join(test_dir, random_image)

download_path = "test_internet_scan.png"

print(f"Bypassed internet security blocks. Copying unseen test CT scan: {random_image}...")
shutil.copy(source_path, download_path)
print("Copy complete!")

print("Running Prediction Pipeline on the CT scan...")
pipeline = PredictionPipeline(download_path)
result = pipeline.predict()

print("\n--- PREDICTION RESULT ---")
print(json.dumps(result, indent=2))
print("-------------------------")
