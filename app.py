from flask import Flask, render_template
from flask_cors import CORS
from config import Config
from routes.convert_routes import convert_routes
from routes.translate_routes import translate_bp
from routes.upload_routes import upload_bp
from models.ai_models import AIModels

app = Flask(__name__)
CORS(app)  # Enable CORS
app.config.from_object(Config)

# Load AI models globally
ai_models = AIModels(cache_dir=Config.CACHE_DIR)

# Register Blueprints
app.register_blueprint(translate_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(convert_routes, url_prefix='/export')
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
