from flask import Blueprint, request, jsonify
from services.translation_service import translate_text

translate_bp = Blueprint('translate_bp', __name__)

@translate_bp.route('/translate', methods=['POST'])
def translate():
    from app import ai_models  # Import the model instance

    data = request.get_json()
    text = data.get('text')
    src_lang = data.get('sourceLang')
    tgt_lang = data.get('targetLang')

    if not all([text, src_lang, tgt_lang]):
        return jsonify({'error': 'Missing required parameters'}), 400

    tokenizer, model, device = ai_models.get_translation_model()
    translated_text = translate_text(text, src_lang, tgt_lang, tokenizer, model, device)
    
    return jsonify({'translation': translated_text})
