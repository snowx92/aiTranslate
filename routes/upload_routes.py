import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from services.pdf_service import extract_text_from_pdf, extract_text_with_ocr
from services.audio_service import transcribe_audio

upload_bp = Blueprint('upload_bp', __name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@upload_bp.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        text = extract_text_from_pdf(filepath) or extract_text_with_ocr(filepath)
        os.remove(filepath)

        return jsonify({'sentences': text}) if text else jsonify({'error': 'Failed to extract text'}), 400

@upload_bp.route('/upload-audio', methods=['POST'])
def upload_audio():
    from app import ai_models  # Import the model instance

    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and file.filename.endswith('.wav'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        text = transcribe_audio(filepath, ai_models.get_whisper_model())

        return jsonify({'text': text}) if text else jsonify({'error': 'Failed to transcribe audio'}), 400
