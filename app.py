import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

def _global_patch_keras():
    def patch_bn_cls(cls):
        if hasattr(cls, '__init__') and not getattr(cls, '_init_patched', False):
            orig_init = cls.__init__
            def patched_init(self, *args, **kwargs):
                if 'axis' in kwargs and isinstance(kwargs['axis'], list):
                    kwargs['axis'] = kwargs['axis'][0]
                orig_init(self, *args, **kwargs)
            cls.__init__ = patched_init
            cls._init_patched = True
        if hasattr(cls, 'from_config') and not getattr(cls, '_fc_patched', False):
            old_fc = cls.from_config
            @classmethod
            def new_fc(c_cls, config):
                if isinstance(config, dict) and 'axis' in config and isinstance(config['axis'], list):
                    config['axis'] = config['axis'][0]
                return old_fc(config)
            cls.from_config = new_fc
            cls._fc_patched = True
            
    def patch_il_cls(cls):
        if hasattr(cls, 'from_config') and not getattr(cls, '_il_fc_patched', False):
            old_fc = cls.from_config
            @classmethod
            def new_fc(c_cls, config):
                if isinstance(config, dict):
                    if 'batch_shape' in config:
                        config['batch_input_shape'] = config.pop('batch_shape')
                    if 'optional' in config:
                        config.pop('optional')
                return old_fc(config)
            cls.from_config = new_fc
            cls._il_fc_patched = True

    for mod_name in ['tensorflow.keras.layers', 'keras.layers', 'tf_keras.layers', 'keras.src.layers.normalization.batch_normalization', 'tensorflow.python.keras.layers.normalization']:
        try:
            mod = __import__(mod_name, fromlist=['BatchNormalization'])
            if hasattr(mod, 'BatchNormalization'):
                patch_bn_cls(mod.BatchNormalization)
        except Exception:
            pass
            
    for mod_name in ['tensorflow.keras.layers', 'keras.layers', 'tf_keras.layers', 'keras.src.engine.input_layer', 'tensorflow.python.keras.engine.input_layer']:
        try:
            mod = __import__(mod_name, fromlist=['InputLayer'])
            if hasattr(mod, 'InputLayer'):
                patch_il_cls(mod.InputLayer)
        except Exception:
            pass

_global_patch_keras()
from Respire.Utils import decodeImage
from flask_cors import CORS, cross_origin
from flask import Flask, request, jsonify, render_template
from Respire.Pipeline.Prediction_Pipeline import PredictionPipeline

os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')

app = Flask(__name__)
CORS(app)

# Security Response Headers (OWASP Compliant)
@app.after_request
def apply_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Optional Sentry Monitoring Integration
sentry_dsn = os.environ.get("SENTRY_DSN")
if sentry_dsn:
    try:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration
        sentry_sdk.init(dsn=sentry_dsn, integrations=[FlaskIntegration()], traces_sample_rate=1.0)
    except ImportError:
        pass

class ClientApp:
    def __init__(self):
        self.filename = "inputImage.jpg"
        self.classifier = PredictionPipeline(self.filename)

clApp = None

def get_client_app():
    global clApp
    if clApp is None:
        clApp = ClientApp()
    return clApp

@app.route("/", methods=['GET'])
@cross_origin()
def home():
    return render_template('index.html')

@app.route("/health", methods=['GET'])
@app.route("/ready", methods=['GET'])
@app.route("/live", methods=['GET'])
@cross_origin()
def healthcheck():
    return jsonify({"status": "ok", "service": "respisense-ml", "version": "v2_fea12bb"}), 200

@app.route("/predict", methods=['POST'])
@cross_origin()
def predictRoute():
    try:
        app_instance = get_client_app()
        image = request.json['image']
        decodeImage(image, app_instance.filename)
        result = app_instance.classifier.predict()
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify([{"image": f"Error: {str(e)}"}]), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)