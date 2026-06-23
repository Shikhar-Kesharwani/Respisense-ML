import os
import tensorflow as tf
from tensorflow.keras.models import load_model

def export_to_saved_model():
    h5_path = os.path.join("Artifacts", "Model_Training", "Trained_Model.h5")
    saved_model_path = os.path.join("Artifacts", "Model_Training", "SavedModel")
    tfjs_model_path = os.path.join("Artifacts", "Model_Training", "TFJS_Model")
    
    print(f"Loading pre-trained model from: {h5_path}")
    model = load_model(h5_path)
    
    print(f"Exporting to enterprise SavedModel format at: {saved_model_path}")
    # Exporting in the SavedModel format is required for TensorFlow Serving (Global Scale)
    model.export(saved_model_path)
    
    print("Exporting to TensorFlow.js format for Edge Inference...")
    try:
        import tensorflowjs as tfjs
        tfjs.converters.save_keras_model(model, tfjs_model_path)
        print(f"TFJS Export Complete at: {tfjs_model_path}")
    except ImportError:
        print("WARNING: tensorflowjs is not installed. Skipping Edge Inference Export.")
        print("To enable TFJS export, run: pip install tensorflowjs")
    
    print("\nExport Pipeline Complete! The model is now ready for high-performance inference.")

if __name__ == "__main__":
    export_to_saved_model()
