import os
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
    return jsonify({"status": "ok", "service": "respisense-ml"}), 200

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