import os
import tensorflow as tf
from tensorflow.keras.models import load_model

saved_model_path = os.path.join("Artifacts", "Model_Training", "SavedModel")
print(f"TF Version: {tf.__version__}")
print(f"File exists: {os.path.exists(saved_model_path)}")
try:
    model = load_model(saved_model_path, compile=False)
    print(type(model))
    if hasattr(model, 'signatures'):
        print(model.signatures)
    print("SUCCESS")
except Exception as e:
    print(f"FAILED: {e}")
