from flask import Flask, render_template, request, jsonify, send_from_directory
import os
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
import fitz  # For PDF text extraction
from pytesseract import image_to_string
from pdf2image import convert_from_path
from werkzeug.utils import secure_filename
import whisper  # Import Whisper

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize the NLLB-200-1.3B model and tokenizer
print("Loading NLLB-200-1.3B model...")
model_name = "facebook/nllb-200-1.3B"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Move model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
print("NLLB-200-1.3B model loaded successfully.")

# Initialize Whisper model
print("Loading Whisper model...")
whisper_model = whisper.load_model("medium")
print("Whisper model loaded successfully.")

# Language configurations
LANG_CODES = {
    "English": "eng_Latn",
    "Arabic": "arb_Arab"
}

def translate_text(text, source_lang, target_lang):
    """
    Translate text using the NLLB-200-1.3B model.
    """
    try:
        # Get source and target language codes
        src_lang_code = LANG_CODES.get(source_lang)
        tgt_lang_code = LANG_CODES.get(target_lang)

        if not src_lang_code or not tgt_lang_code:
            raise ValueError("Unsupported language pair")

        # Tokenize the input text with the source language tag
        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Get the token ID for the target language
        # NLLB requires the language token at the beginning of the generated sequence
        forced_bos_token = tgt_lang_code
        
        # Generate translation
        with torch.no_grad():
            translated_ids = model.generate(
                **inputs,
                forced_bos_token_id=tokenizer.convert_tokens_to_ids(forced_bos_token),
                max_length=512,
                num_beams=4,
                length_penalty=0.6,
                early_stopping=True
            )

        # Decode the translated text
        translated_text = tokenizer.decode(translated_ids[0], skip_special_tokens=True)
        return translated_text

    except Exception as e:
        print(f"Translation error: {str(e)}")
        raise

def extract_text_from_pdf(file_path):
    """Extract text from searchable PDFs."""
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            text += page.get_text()
    return text

def extract_text_with_ocr(file_path):
    """Extract text from non-searchable PDFs using OCR."""
    images = convert_from_path(file_path)
    text = ""
    for image in images:
        text += image_to_string(image, lang="ara+eng")
    return text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()
        text = data.get('text')
        src_lang = data.get('sourceLang')
        tgt_lang = data.get('targetLang')

        if not all([text, src_lang, tgt_lang]):
            return jsonify({'error': 'Missing required parameters'}), 400

        translated_text = translate_text(text, src_lang, tgt_lang)
        return jsonify({'translation': translated_text})

    except Exception as e:
        print("Translation error:", str(e))
        return jsonify({'error': str(e)}), 400

@app.route('/upload-pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Extract text from PDF
            text = extract_text_from_pdf(filepath)
            if not text.strip():  # If no text is found, use OCR
                text = extract_text_with_ocr(filepath)

            return jsonify({'text': text})

        except Exception as e:
            return jsonify({'error': str(e)}), 400

        finally:
            # Clean up the file
            if os.path.exists(filepath):
                os.remove(filepath)

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if file and file.filename.endswith('.wav'):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Transcribe audio using Whisper
            result = whisper_model.transcribe(filepath)
            return jsonify({'text': result['text']})

        except Exception as e:
            return jsonify({'error': str(e)}), 400

        finally:
            # Clean up the file
            if os.path.exists(filepath):
                os.remove(filepath)

    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=False, host='0.0.0.0', port=5000)