from flask import Blueprint, request
from services.convert_service import export_to_excel, export_to_word, export_to_pdf_table, export_to_word_text, export_to_pdf_text

convert_routes = Blueprint('convert_routes', __name__)

@convert_routes.route("/excel", methods=["POST"])
def export_excel():
    chat_data = request.json.get("chat_data", [])
    return export_to_excel(chat_data)

@convert_routes.route("/word", methods=["POST"])
def export_word():
    chat_data = request.json.get("chat_data", [])
    return export_to_word(chat_data)

@convert_routes.route("/pdf_table", methods=["POST"])
def export_pdf_table():
    chat_data = request.json.get("chat_data", [])
    return export_to_pdf_table(chat_data)

@convert_routes.route("/word_text", methods=["POST"])
def export_word_text():
    chat_data = request.json.get("chat_data", [])
    return export_to_word_text(chat_data)

@convert_routes.route("/pdf_text", methods=["POST"])
def export_pdf_text():
    chat_data = request.json.get("chat_data", [])
    return export_to_pdf_text(chat_data)