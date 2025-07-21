import os
from flask import Blueprint, request, jsonify, send_file
from werkzeug.utils import secure_filename
from services.pdf_service import extract_text_from_pdf, extract_text_with_ocr
from services.audio_service import transcribe_audio, text_to_speech, save_audio_file
from io import BytesIO
import uuid

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

    # Accept multiple audio formats
    allowed_extensions = ['.wav', '.mp3', '.m4a', '.ogg', '.flac']
    if file and any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        try:
            whisper_model_info = ai_models.get_whisper_model()
            text = transcribe_audio(filepath, whisper_model_info)
            return jsonify({'text': text})
        except Exception as e:
            # Clean up file if transcription fails
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Unsupported audio format. Please use WAV, MP3, M4A, OGG, or FLAC.'}), 400

@upload_bp.route('/text-to-speech', methods=['POST'])
def convert_text_to_speech():
    from app import ai_models  # Import the model instance
    
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided'}), 400
        
        text = data['text'].strip()
        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        # Get optional parameters
        voice = data.get('voice', 'alloy')  # alloy, echo, fable, onyx, nova, shimmer
        model = data.get('model', 'tts-1')  # tts-1 or tts-1-hd
        
        # Validate voice option
        valid_voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
        if voice not in valid_voices:
            voice = 'alloy'  # Default fallback
        
        # Get OpenAI API key
        api_key = ai_models.openai_api_key
        if not api_key:
            return jsonify({'error': 'OpenAI API key not configured'}), 500
        
        # Generate audio
        audio_data = text_to_speech(text, voice=voice, model=model, api_key=api_key)
        
        # Create a BytesIO object to serve the audio
        audio_buffer = BytesIO(audio_data)
        audio_buffer.seek(0)
        
        return send_file(
            audio_buffer,
            mimetype='audio/mpeg',
            as_attachment=True,
            download_name='speech.mp3'
        )
        
    except Exception as e:
        return jsonify({'error': f'Text-to-speech failed: {str(e)}'}), 500
