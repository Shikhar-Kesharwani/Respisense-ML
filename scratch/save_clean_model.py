import tensorflow as tf
from tensorflow.keras.models import load_model

print(f"Running with TF Version: {tf.__version__}")

saved_model_path = "Artifacts/Model_Training/SavedModel"
output_path = "Artifacts/Model_Training/clean_model.h5"

print("Loading SavedModel...")
model = load_model(saved_model_path, compile=False)

print("Saving to clean .h5 format natively...")
model.save(output_path, save_format='h5')

print("Done! Clean model saved to", output_path)
