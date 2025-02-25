from graphviz import Digraph

# Create a directed graph with a modern style
dot = Digraph("AI_Translator", format="png")

# Graph attributes for better design
dot.attr(rankdir="TB", splines="ortho", bgcolor="#F9F9F9")
dot.attr("node", shape="rect", style="filled", fillcolor="white", fontname="Arial", fontsize="12", color="#2C3E50")
dot.attr("edge", color="#3498DB", penwidth="2")

# User Input Section
dot.node("User", "User", shape="ellipse", fillcolor="#2ECC71", fontcolor="white", style="filled")
dot.node("Select_Language", "Select Source & Target Language", fillcolor="#E67E22", fontcolor="white")
dot.node("Input_Options", "Choose Input Method", fillcolor="#E67E22", fontcolor="white")
dot.edge("User", "Select_Language", penwidth="2")
dot.edge("Select_Language", "Input_Options", penwidth="2")

# Input Methods
dot.node("Text_Input", "Text Input", fillcolor="#3498DB", fontcolor="white")
dot.node("PDF_Upload", "Upload PDF", fillcolor="#3498DB", fontcolor="white")
dot.node("Speech_Input", "Speech Input (Speech-to-Text)", fillcolor="#3498DB", fontcolor="white")
dot.edge("Input_Options", "Text_Input")
dot.edge("Input_Options", "PDF_Upload")
dot.edge("Input_Options", "Speech_Input")

# PDF Processing
dot.node("Check_PDF_Type", "Check PDF Type", fillcolor="#9B59B6", fontcolor="white")
dot.node("Extract_Text", "Extract Text (If Text-Based)", fillcolor="#9B59B6", fontcolor="white")
dot.node("Use_OCR", "Use OCR (If Image-Based)", fillcolor="#9B59B6", fontcolor="white")
dot.edge("PDF_Upload", "Check_PDF_Type")
dot.edge("Check_PDF_Type", "Extract_Text", label="Text PDF", color="#2ECC71")
dot.edge("Check_PDF_Type", "Use_OCR", label="Image PDF", color="#E74C3C")

# Processing & Translation
dot.node("Translate", "Translate Text Sequence by Sequence", fillcolor="#1ABC9C", fontcolor="white")
dot.edge("Text_Input", "Translate")
dot.edge("Extract_Text", "Translate")
dot.edge("Use_OCR", "Translate")
dot.edge("Speech_Input", "Translate")

# Output Options
dot.node("Chat_Display", "Display in Chat Format", fillcolor="#F1C40F", fontcolor="black")
dot.node("Export_Excel", "Export to Excel (Original & Translated Text)", fillcolor="#F1C40F", fontcolor="black")
dot.edge("Translate", "Chat_Display")
dot.edge("Translate", "Export_Excel")

# Render the diagram
dot


# Save the diagram
file_path = "AI_Translator_Diagram"
dot.render(file_path, format="png", cleanup=True)