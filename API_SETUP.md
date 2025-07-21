# API Setup Guide for AI Translator

This application now uses online APIs instead of downloading large models locally. You need to set up the following API keys:

## Required API Keys

### 1. Hugging Face API Token
- **Purpose**: Used for text translation via NLLB-200-1.3B model
- **How to get**: 
  1. Go to [Hugging Face Settings](https://huggingface.co/settings/tokens)
  2. Create a new token with "Read" permissions
  3. Copy the token

### 2. OpenAI API Key
- **Purpose**: Used for audio transcription via Whisper API
- **How to get**:
  1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
  2. Create a new API key
  3. Copy the key (you won't be able to see it again)

## Setting Up Environment Variables

### Option 1: Environment Variables (Recommended)
Set these environment variables in your system:

```bash
# Windows (PowerShell)
$env:HUGGINGFACE_API_TOKEN="your_token_here"
$env:OPENAI_API_KEY="your_key_here"

# Windows (Command Prompt)
set HUGGINGFACE_API_TOKEN=your_token_here
set OPENAI_API_KEY=your_key_here

# Linux/Mac
export HUGGINGFACE_API_TOKEN="your_token_here"
export OPENAI_API_KEY="your_key_here"
```

### Option 2: .env File
Create a `.env` file in the aiTranslate directory with:

```
HUGGINGFACE_API_TOKEN=your_token_here
OPENAI_API_KEY=your_key_here
```

## Benefits of Online APIs

- ✅ No large model downloads (saves several GB of space)
- ✅ Always up-to-date models
- ✅ Faster startup time
- ✅ Lower memory usage
- ✅ Access to latest model improvements

## Cost Considerations

- **Hugging Face Inference API**: Free tier available, pay-per-request for heavy usage
- **OpenAI Whisper API**: Pay-per-minute of audio transcribed

## Running the Application

After setting up your API keys:

```bash
pip install -r requirements.txt
python app.py
```

The application will start and use online APIs for translation and transcription. 