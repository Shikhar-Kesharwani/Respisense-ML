import os
import tensorflow as tf
from tensorflow.keras.models import load_model

h5_path = os.path.join("Artifacts", "Model_Training", "Trained_Model.h5")
model = load_model(h5_path)

# The model is a Sequential or Functional model. Let's find the base model layer.
for layer in model.layers:
    print(layer.name, layer.__class__.__name__)
    if isinstance(layer, tf.keras.Model):
        print("  Base model layers:")
        for l in layer.layers[-10:]:
            print("  -", l.name)
