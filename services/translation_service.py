import requests
import re

LANG_CODES = {
    "English": "en",
    "Arabic": "ar"
}

def translate_text(text, source_lang, target_lang, model_info):
    """
    Translate text using online models (Hugging Face Inference API)
    
    Args:
        text: Text to translate
        source_lang: Source language name
        target_lang: Target language name
        model_info: Dictionary containing API info from AIModels.get_translation_model()
    """
    try:
        if model_info.get('type') != 'huggingface_api':
            raise ValueError("Unsupported model type for translation")
        
        api_token = model_info.get('api_token')
        models = model_info.get('models')
        
        if not api_token:
            raise ValueError("Hugging Face API token is required for online translation")
        
        src_lang_code = LANG_CODES.get(source_lang)
        tgt_lang_code = LANG_CODES.get(target_lang)

        if not src_lang_code or not tgt_lang_code:
            raise ValueError("Unsupported language pair")

        # Determine which model to use based on language direction
        if src_lang_code == "en" and tgt_lang_code == "ar":
            model_url = models["en_to_ar"]
        elif src_lang_code == "ar" and tgt_lang_code == "en":
            model_url = models["ar_to_en"]
        else:
            raise ValueError(f"Unsupported translation direction: {source_lang} to {target_lang}")

        headers = {"Authorization": f"Bearer {api_token}"}
        
        # Helsinki-NLP models use simple input format
        payload = {
            "inputs": text
        }
        
        response = requests.post(model_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get('translation_text', text)
        return text
    
    except Exception as e:
        print(f"Translation error: {str(e)}")
        raise

def translate_text_legacy(text, source_lang, target_lang, tokenizer, model, device):
    """
    Legacy function for backward compatibility with local models
    This function is deprecated - use translate_text() with model_info instead
    """
    import torch
    
    try:
        src_lang_code = LANG_CODES.get(source_lang)
        tgt_lang_code = LANG_CODES.get(target_lang)

        if not src_lang_code or not tgt_lang_code:
            raise ValueError("Unsupported language pair")

        inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        forced_bos_token = tgt_lang_code
        
        with torch.no_grad():
            translated_ids = model.generate(
                **inputs,
                forced_bos_token_id=tokenizer.convert_tokens_to_ids(forced_bos_token),
                max_length=1024,
                num_beams=5,
                length_penalty=1.0,
                do_sample=False
            )

        return tokenizer.decode(translated_ids[0], skip_special_tokens=True)
    
    except Exception as e:
        print(f"Translation error: {str(e)}")
        raise
