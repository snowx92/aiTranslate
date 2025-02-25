import os

def transcribe_audio(file_path, whisper_model):
    try:
        result = whisper_model.transcribe(file_path)
        return result['text']
    except Exception as e:
        print(f"Audio transcription error: {str(e)}")
        return None
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
