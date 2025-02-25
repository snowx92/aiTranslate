import torch
from transformers import AutoTokenizer
import re

LANG_CODES = {
    "English": "eng_Latn",
    "Arabic": "arb_Arab"
}

def translate_text(text, source_lang, target_lang, tokenizer, model, device):
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
