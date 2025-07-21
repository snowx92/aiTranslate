import os
from flask import Flask, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from config import Config
from routes.convert_routes import convert_routes
from routes.translate_routes import translate_bp
from routes.upload_routes import upload_bp
from models.ai_models import AIModels

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS
app.config.from_object(Config)

# Load AI models globally - now using online APIs
ai_models = AIModels()

# Register Blueprints
app.register_blueprint(translate_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(convert_routes, url_prefix='/export')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # Production configuration for deployment
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug, host='0.0.0.0', port=port)
