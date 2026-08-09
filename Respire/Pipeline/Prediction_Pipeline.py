import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
import cv2
import base64


class PredictionPipeline:
    def __init__(self,filename):
        self.filename =filename
        
    def _is_valid_ct_scan(self, filepath):
        """
        Heuristic out-of-distribution check to ensure input image is a valid Chest CT scan.
        Chest CT scans are grayscale (RGB values are nearly identical across channels).
        Variance of differences between channels (R, G, B) should be minimal (< 10.0).
        """
        try:
            img = Image.open(filepath).convert('RGB')
        except Exception:
            return False
        
        # Convert to signed 16-bit to prevent underflow/overflow during subtraction
        img_arr = np.array(img, dtype=np.int16)
        r = img_arr[:, :, 0]
        g = img_arr[:, :, 1]
        b = img_arr[:, :, 2]
        
        # Calculate variance of differences between channels
        color_diff_var = np.var(r - g) + np.var(r - b) + np.var(g - b)
        
        # A true grayscale image has variance 0. We allow a tiny tolerance for compression artifacts.
        if color_diff_var > 10.0:
            return False
            
        return True
        
    def _make_gradcam_heatmap(self, img_array, model, last_conv_layer_name="post_relu", pred_index=None):
        grad_model = tf.keras.models.Model(
            model.inputs, [model.get_layer(last_conv_layer_name).output, model.output]
        )

        with tf.GradientTape() as tape:
            last_conv_layer_output, preds = grad_model(img_array)
            if pred_index is None:
                pred_index = tf.argmax(preds[0])
            class_channel = preds[:, pred_index]

        grads = tape.gradient(class_channel, last_conv_layer_output)
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        last_conv_layer_output = last_conv_layer_output[0]
        heatmap = last_conv_layer_output @ pooled_grads[..., tf.newaxis]
        heatmap = tf.squeeze(heatmap)
        
        # Add 1e-10 to the denominator to mathematically prevent division by zero (NaN errors)
        heatmap = tf.maximum(heatmap, 0) / (tf.math.reduce_max(heatmap) + 1e-10)
        return heatmap.numpy()

    def _save_and_display_gradcam(self, img_path, heatmap, alpha=0.4):
        img = cv2.imread(img_path)
        heatmap = np.uint8(255 * heatmap)
        jet = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
        jet = cv2.resize(jet, (img.shape[1], img.shape[0]))
        superimposed_img = jet * alpha + img
        superimposed_img = np.clip(superimposed_img, 0, 255).astype(np.uint8)
        _, buffer = cv2.imencode('.jpg', superimposed_img)
        return base64.b64encode(buffer).decode('utf-8')
    
    def predict(self):
        # 1. Out-of-Distribution Rejection Check
        if not self._is_valid_ct_scan(self.filename):
            return [{ "image" : "Rejected: Please upload a valid Chest CT Scan."}]
            
        model = load_model(os.path.join("Artifacts","Model_Training", "Trained_Model.h5"), compile=False)

        imagename = self.filename
        test_image = image.load_img(imagename, target_size = (224,224))
        test_image = image.img_to_array(test_image)
        test_image = np.expand_dims(test_image, axis = 0)
        
        # 3. Predict
        preds = model.predict(test_image)
        result = np.argmax(preds, axis=1)
        print("Prediction Array Output:", result)
        
        # 4. Generate Grad-CAM Heatmap
        try:
            heatmap = self._make_gradcam_heatmap(test_image, model, last_conv_layer_name="post_relu")
            heatmap_base64 = self._save_and_display_gradcam(self.filename, heatmap)
        except Exception as e:
            print("Error generating Grad-CAM:", e)
            heatmap_base64 = ""

        if result[0] == 1:
            prediction = 'Normal'
        else:
            prediction = 'Adenocarcinoma Cancer'
            
        return [{ "image" : prediction, "heatmap": heatmap_base64}]