import PyPDF2
import re
import os

def chunk_text_by_sentence(text):
    """Splits text into sentences, handling Arabic & English punctuation correctly."""
    normalized_text = text.replace("\n", " ")  # Remove line breaks
    normalized_text = re.sub(r'([.!?])(?=\S)', r'\1 ', normalized_text)  # Ensure space after punctuation
    return re.split(r'(?<=[.!?])\s+', normalized_text.strip()) if text else []

def extract_text_from_pdf(file_path):
    """Extracts text from a PDF using PyPDF2."""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text.strip():
                    text += page_text + " "
    except Exception as e:
        print(f"Error reading PDF with PyPDF2: {e}")
        return []
    
    print("Extracted Text from PyPDF2:", text[:200] + "..." if len(text) > 200 else text)  # Debugging
    return chunk_text_by_sentence(text) if text.strip() else []

def extract_text_with_ocr(file_path):
    """
    Extracts text from image-based PDFs using OCR.
    Note: This requires pdf2image and pytesseract which need additional setup.
    """
    try:
        # Optional import - only works if packages are installed
        from pdf2image import convert_from_path
        from pytesseract import image_to_string
        
        images = convert_from_path(file_path, dpi=300)
        text = ""
        
        for i, image in enumerate(images):
            image_text = image_to_string(image, lang="ara+eng")
            print(f"OCR Extracted Text from Page {i+1}: {image_text[:100]}..." if len(image_text) > 100 else image_text)
            text += image_text + " "

        return chunk_text_by_sentence(text) if text.strip() else []
        
    except ImportError:
        print("Warning: OCR functionality not available. Install pdf2image and pytesseract for OCR support.")
        return []
    except Exception as e:
        print(f"Error with OCR: {e}")
        return []

def extract_text_from_pdf_file(filepath):
    """Combines PyPDF2 and optional OCR methods to extract text from PDFs."""
    text = extract_text_from_pdf(filepath)

    if not text:  # If no text extracted, try OCR if available
        print("No text extracted using PyPDF2, trying OCR...")
        text = extract_text_with_ocr(filepath)
        if not text:
            print("OCR not available or failed. Please install pdf2image and pytesseract for image-based PDF support.")

    return text
