import os
import pandas as pd
from io import BytesIO
from flask import send_file, jsonify, make_response
from docx import Document
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import os
from io import BytesIO
from flask import send_file, jsonify, make_response
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
def format_text(text, language):

    return text

def export_to_excel(chat_data):
    if not chat_data:
        return jsonify({"error": "No messages to export"}), 400

    df = pd.DataFrame(chat_data, columns=["Original Text", "Translated Text"])

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, sheet_name="Chat Export", index=False)
        workbook = writer.book
        worksheet = writer.sheets["Chat Export"]

        # Set column width
        for i, col in enumerate(df.columns):
            max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
            worksheet.set_column(i, i, max_len)

        # Center text and apply header format
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)

    output.seek(0)

    response = make_response(send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="translated_chat.xlsx"
    ))

    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response

def export_to_word(chat_data):
    if not chat_data:
        return jsonify({"error": "No messages to export"}), 400

    doc = Document()
    table = doc.add_table(rows=1, cols=2)
    table.style = "Table Grid"

    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Original Text"
    hdr_cells[1].text = "Translated Text"

    for row in chat_data:
        row_cells = table.add_row().cells
        row_cells[0].text = format_text(str(row[0]), 'english')
        row_cells[1].text = format_text(str(row[1]), 'arabic')

    output = BytesIO()
    doc.save(output)
    output.seek(0)
    
    response = make_response(send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name="translated_chat.docx"
    ))
    
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response


def export_to_word_text(chat_data):
    if not chat_data:
        return jsonify({"error": "No messages to export"}), 400

    doc = Document()
    
    for row in chat_data:
        translated_text = format_text(str(row[1]), 'arabic')  # Only translated text
        
        p = doc.add_paragraph()
        run = p.add_run(translated_text)
        run.bold = True  # Make text bold

        doc.add_paragraph("")  # Add space

    output = BytesIO()
    doc.save(output)
    output.seek(0)

    response = make_response(send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name="translated_chat_text.docx"
    ))

    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response

# Register arial font
font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'arial.ttf')
pdfmetrics.registerFont(TTFont('arial', font_path))


def reshape_arabic(text):
    """Fix Arabic text display issues (inversion & spacing)."""
    return get_display(arabic_reshaper.reshape(text))

import textwrap

def export_to_pdf_text(chat_data):
    if not chat_data:
        return jsonify({"error": "No messages to export"}), 400

    output = BytesIO()
    pdf = canvas.Canvas(output, pagesize=A4)
    pdf.setFont("Helvetica", 12)

    y_position = 800  # Start position for text
    max_width = 450  # Adjust max width for text wrapping

    for row in chat_data:
        translated_text = reshape_arabic(str(row[1]))  # Reshape Arabic text

        # Wrap text
        wrapped_text = textwrap.wrap(translated_text, width=70)  # Adjust width as needed

        for line in wrapped_text:
            pdf.drawRightString(500, y_position, line)  # Right-aligned for Arabic
            y_position -= 20  # Move down

            if y_position < 50:  # If at bottom, create new page
                pdf.showPage()
                pdf.setFont("Helvetica", 12)
                y_position = 800

    pdf.save()
    output.seek(0)

    response = make_response(send_file(
        output,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="translated_chat_text.pdf"
    ))

    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response

def export_to_pdf_table(chat_data):
    if not chat_data:
        return jsonify({"error": "No messages to export"}), 400

    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    elements = []
    
    styles = getSampleStyleSheet()
    styleN = styles["Normal"]

    data = [["Original Text", "Translated Text"]]  # Table Header

    for row in chat_data:
        original_text = Paragraph(str(row[0]), styleN)
        translated_text = Paragraph(reshape_arabic(str(row[1])), styleN)  # Fix Arabic text order
        data.append([original_text, translated_text])

    # Define table style
    table = Table(data, colWidths=[250, 250])  # Ensure columns have enough width
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), "Helvetica"),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),  # Ensures multi-line text is visible
    ])
    table.setStyle(style)

    elements.append(table)
    doc.build(elements)

    output.seek(0)
    response = make_response(send_file(
        output,
        mimetype="application/pdf",
        as_attachment=True,
        download_name="translated_chat_table.pdf"
    ))

    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    return response