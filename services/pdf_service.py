import fitz
import re
import os
from pdf2image import convert_from_path
from pytesseract import image_to_string

def chunk_text_by_sentence(text):
    """Splits text into sentences, handling Arabic & English punctuation correctly."""
    normalized_text = text.replace("\n", " ")  # Remove line breaks
    normalized_text = re.sub(r'([.!?])(?=\S)', r'\1 ', normalized_text)  # Ensure space after punctuation
    return re.split(r'(?<=[.!?])\s+', normalized_text.strip()) if text else []

def extract_text_from_pdf(file_path):
    """Extracts text from a PDF using PyMuPDF (fitz)."""
    text = ""
    with fitz.open(file_path) as pdf:
        for page in pdf:
            page_text = page.get_text("text")
            if page_text.strip():
                text += page_text + " "
    
    print("Extracted Text from PyMuPDF:", text)  # Debugging
    return chunk_text_by_sentence(text) if text.strip() else []

def extract_text_with_ocr(file_path):
    """Extracts text from image-based PDFs using OCR."""
    images = convert_from_path(file_path, dpi=300)  # Increase DPI for better accuracy
    text = ""
    
    for i, image in enumerate(images):
        image_text = image_to_string(image, lang="ara+eng")
        print(f"OCR Extracted Text from Page {i+1}: {image_text}")  # Debugging
        text += image_text + " "

    return chunk_text_by_sentence(text) if text.strip() else []

def extract_text_from_pdf_file(filepath):
    """Combines PyMuPDF and OCR methods to extract text from PDFs."""
    text = extract_text_from_pdf(filepath)

    if not text:  # If no text extracted, try OCR
        print("No text extracted using PyMuPDF, switching to OCR...")
        text = extract_text_with_ocr(filepath)

    return text
