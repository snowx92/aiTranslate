import requests
import openai
from typing import Optional
import os

class AIModels:
    def __init__(self, hf_api_token: Optional[str] = None, openai_api_key: Optional[str] = None):
        """
        Initialize AI Models with API tokens for online inference
        
        Args:
            hf_api_token: Hugging Face API token for inference API
            openai_api_key: OpenAI API key for Whisper API
        """
        # Hugging Face settings
        self.hf_api_token = hf_api_token or os.getenv('HUGGINGFACE_API_TOKEN')
        
        # Use better quality Helsinki-NLP models for translation
        self.translation_models = {
            "en_to_ar": "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-tc-big-en-ar",  # UPGRADED: Better quality model
            "ar_to_en": "https://api-inference.huggingface.co/models/Helsinki-NLP/opus-mt-ar-en"
        }
        
        # OpenAI settings for Whisper
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        
        if self.hf_api_token:
            print(f"AI Models initialized for online inference.")
            print(f"Hugging Face API token loaded: {self.hf_api_token[:8]}...")
        
        if self.openai_api_key:
            print(f"OpenAI API key loaded: {self.openai_api_key[:8]}...")

    def get_translation_model(self):
        """
        Returns translation model configuration for the translation service
        """
        return {
            'type': 'huggingface_api',
            'models': self.translation_models,
            'api_token': self.hf_api_token
        }

    def get_whisper_model(self):
        """
        Returns Whisper model configuration for the audio service
        """
        return {
            'type': 'openai_api',
            'api_key': self.openai_api_key,
            'model': 'whisper-1'
        }

    def translate_text_online(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translate text using Hugging Face Inference API with improved Helsinki-NLP models
        """
        if not self.hf_api_token:
            raise ValueError("Hugging Face API token is required for online translation")
        
        headers = {"Authorization": f"Bearer {self.hf_api_token}"}
        
        # Determine model based on language direction
        if source_lang == "English" and target_lang == "Arabic":
            model_url = self.translation_models["en_to_ar"]
        elif source_lang == "Arabic" and target_lang == "English":
            model_url = self.translation_models["ar_to_en"]
        else:
            raise ValueError(f"Unsupported language pair: {source_lang} → {target_lang}")
        
        payload = {"inputs": text}
        
        try:
            response = requests.post(model_url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                if 'translation_text' in result[0]:
                    return result[0]['translation_text']
                elif 'generated_text' in result[0]:
                    return result[0]['generated_text']
            
            return str(result) if result else "Translation failed"
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Translation API error: {str(e)}")

    def transcribe_audio_online(self, audio_file_path: str) -> str:
        """
        Transcribe audio using OpenAI's Whisper API
        """
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for audio transcription")
        
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.openai_api_key)
            
            with open(audio_file_path, 'rb') as audio_file:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language="ar"  # Specify Arabic for better accuracy
                )
                return response.text
        except Exception as e:
            raise Exception(f"Audio transcription error: {str(e)}")
