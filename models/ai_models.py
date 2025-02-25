import torch
import whisper
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

class AIModels:
    def __init__(self, cache_dir):
        print("Loading NLLB-200-1.3B model...")
        model_name = "facebook/nllb-200-1.3B"
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True, cache_dir=cache_dir)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name, local_files_only=True, cache_dir=cache_dir)
        
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self.model.to(self.device)
        print("NLLB-200-1.3B model loaded successfully.")

        print("Loading Whisper model...")
        self.whisper_model = whisper.load_model("medium")
        print("Whisper model loaded successfully.")

    def get_translation_model(self):
        return self.tokenizer, self.model, self.device

    def get_whisper_model(self):
        return self.whisper_model
