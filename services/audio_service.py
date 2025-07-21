import os
import requests
import time
from pathlib import Path

def transcribe_audio(file_path, whisper_model_info):
    """
    Transcribe audio using OpenAI Whisper API (STT - Speech to Text)
    
    Args:
        file_path: Path to audio file
        whisper_model_info: Dictionary containing model info from AIModels.get_whisper_model()
    """
    try:
        if whisper_model_info.get('type') == 'openai_api':
            api_key = whisper_model_info.get('api_key')
            if not api_key:
                raise ValueError("OpenAI API key not available for audio transcription")
            
            # Use direct API call instead of client to avoid httpx issues
            headers = {
                'Authorization': f'Bearer {api_key}'
            }
            
            with open(file_path, "rb") as audio_file:
                files = {
                    'file': audio_file,
                    'model': (None, 'whisper-1'),
                    'language': (None, 'ar')  # Arabic for better accuracy
                }
                
                # Retry logic for rate limiting
                max_retries = 3
                base_delay = 1
                
                for attempt in range(max_retries):
                    response = requests.post(
                        'https://api.openai.com/v1/audio/transcriptions',
                        headers=headers,
                        files=files,
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return result.get('text', '')
                    elif response.status_code == 429:
                        if attempt < max_retries - 1:
                            # Exponential backoff: wait 1s, 2s, 4s
                            wait_time = base_delay * (2 ** attempt)
                            print(f"Rate limit hit, waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                            time.sleep(wait_time)
                            continue
                        else:
                            raise Exception("Rate limit exceeded. Please wait a few minutes before trying again.")
                    else:
                        response.raise_for_status()  # Raise for other HTTP errors
                
        else:
            raise ValueError("Unsupported whisper model type. Only OpenAI API is supported.")
                
    except Exception as e:
        print(f"Audio transcription error: {str(e)}")
        raise Exception(f"Audio transcription failed: {str(e)}")
    finally:
        # Clean up uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

def text_to_speech(text, voice="alloy", model="tts-1", api_key=None):
    """
    Convert text to speech using OpenAI TTS API (TTS - Text to Speech)
    Uses direct API calls to bypass OpenAI client initialization issues
    
    Args:
        text: Text to convert to speech
        voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
        model: TTS model to use (tts-1 or tts-1-hd)
        api_key: OpenAI API key
    
    Returns:
        bytes: Audio data in MP3 format
    """
    try:
        if not api_key:
            raise ValueError("OpenAI API key is required for text-to-speech")
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': model,
            'input': text,
            'voice': voice,
            'response_format': 'mp3'
        }
        
        # Retry logic for rate limiting
        max_retries = 3
        base_delay = 1
        
        for attempt in range(max_retries):
            response = requests.post(
                'https://api.openai.com/v1/audio/speech',
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                return response.content
            elif response.status_code == 429:
                if attempt < max_retries - 1:
                    # Exponential backoff: wait 1s, 2s, 4s
                    wait_time = base_delay * (2 ** attempt)
                    print(f"TTS rate limit hit, waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception("Rate limit exceeded. Please wait a few minutes before trying TTS again.")
            else:
                response.raise_for_status()  # Raise for other HTTP errors
        
    except Exception as e:
        print(f"Text-to-speech error: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        raise Exception(f"Text-to-speech failed: {str(e)}")

def save_audio_file(audio_data, filename, upload_folder="uploads"):
    """
    Save audio data to file
    
    Args:
        audio_data: Audio bytes data
        filename: Name for the audio file
        upload_folder: Directory to save the file
    
    Returns:
        str: Path to saved file
    """
    try:
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        
        with open(file_path, "wb") as f:
            f.write(audio_data)
        
        return file_path
        
    except Exception as e:
        print(f"Audio file save error: {str(e)}")
        raise Exception(f"Failed to save audio file: {str(e)}")
