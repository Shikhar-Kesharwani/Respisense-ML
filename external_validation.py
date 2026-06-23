import os
import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import glob

# ==============================================================================
# THESIS LAYER 5: EXTERNAL VALIDATION (DOMAIN SHIFT ANALYSIS)
# ==============================================================================
# This script loads your trained model and evaluates it on a completely unseen
# external dataset (e.g., CheXpert or Kaggle). It calculates the clinical metrics
# required for your thesis defense.
# ==============================================================================

def load_and_preprocess_image(img_path):
    img = tf.keras.preprocessing.image.load_img(img_path, target_size=(224, 224))
    img_array = tf.keras.preprocessing.image.img_to_array(img)
    img_array = img_array / 255.0  # Normalize to [0,1]
    return img_array

def run_external_validation():
    print("\n" + "="*60)
    print("STARTING EXTERNAL VALIDATION (DOMAIN SHIFT ANALYSIS)")
    print("="*60)

    model_path = os.path.join("Artifacts", "Model_Training", "Trained_Model.h5")
    if not os.path.exists(model_path):
        print(f"[ERROR] Trained model not found at {model_path}")
        return

    print("Loading Trained Model...")
    model = tf.keras.models.load_model(model_path)

    # Define the external data directory
    external_data_dir = os.path.join("Artifacts", "External_Validation_Data")
    if not os.path.exists(external_data_dir):
        print(f"\n[WARNING] Directory {external_data_dir} does not exist.")
        print("To run this test, create the folder and place 'Normal' and 'Adenocarcinoma' subfolders inside.")
        return

    # Assuming subdirectories are the class names
    classes = sorted(os.listdir(external_data_dir))
    if len(classes) != 2:
        print("[ERROR] External validation requires exactly 2 class subdirectories (e.g., Normal, Adenocarcinoma)")
        return

    class_map = {classes[0]: 0, classes[1]: 1}
    
    y_true = []
    X_external = []

    print(f"Scanning {external_data_dir} for unseen medical images...")
    for class_name in classes:
        class_dir = os.path.join(external_data_dir, class_name)
        for img_name in os.listdir(class_dir):
            if img_name.endswith(('.png', '.jpg', '.jpeg')):
                img_path = os.path.join(class_dir, img_name)
                X_external.append(load_and_preprocess_image(img_path))
                y_true.append(class_map[class_name])

    if len(X_external) == 0:
        print(f"\n[WARNING] No images found in {external_data_dir}.")
        return

    X_external = np.array(X_external)
    y_true = np.array(y_true)

    print(f"Total External Images Loaded: {len(X_external)}")
    print("Running Inference on External Dataset...")
    
    # Predict
    y_pred_proba = model.predict(X_external)
    y_pred = np.argmax(y_pred_proba, axis=1)

    # Calculate Thesis Metrics
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    cm = confusion_matrix(y_true, y_pred)

    print("\n" + "="*50)
    print("EXTERNAL VALIDATION RESULTS")
    print("="*50)
    print(f"Accuracy:  {acc*100:.2f}%")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f} (Crucial for Medical AI)")
    print(f"F1-Score:  {f1:.4f}")
    print("Confusion Matrix:")
    print(cm)

    # Domain Shift Analysis (Assuming internal CV accuracy was ~96.2%)
    internal_acc = 0.962
    domain_shift = (internal_acc - acc) * 100

    print("\nDomain Shift Analysis:")
    print(f"  Internal Validation Accuracy: 96.20%")
    print(f"  External Validation Accuracy: {acc*100:.2f}%")
    print(f"  Domain Shift Difference:      {domain_shift:.2f}%")

    if domain_shift < 5:
        print("  ✓ EXCELLENT: Model generalizes well across domains. Ready for Hospital Deployment.")
    elif domain_shift < 10:
        print("  ✓ GOOD: Acceptable generalization for production.")
    elif domain_shift < 20:
        print("  ⚠ MODERATE: Domain shift present. Investigate specific misclassifications.")
    else:
        print("  ✗ BAD: Severe domain shift. Model memorized internal hospital protocols.")

if __name__ == "__main__":
    run_external_validation()
