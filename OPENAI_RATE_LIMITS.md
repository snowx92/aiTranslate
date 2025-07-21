# OpenAI API Rate Limits & Usage Guide

## 🚨 Rate Limit Error (429) - What It Means

When you see "429 Client Error: Too Many Requests", it means you've hit OpenAI's API rate limits. This is normal and can be managed.

## 📊 OpenAI API Limits by Plan

### **Free Tier ($5 credit)**
- **STT (Whisper)**: ~25 requests per minute
- **TTS**: ~5 requests per minute  
- **Total monthly**: $5 worth of usage

### **Pay-as-you-go**
- **STT (Whisper)**: ~50 requests per minute
- **TTS**: ~10 requests per minute
- **Monthly billing**: Based on usage

### **Plus ($20/month)**
- **Higher limits**: ~100 requests per minute
- **Priority access**: Better availability
- **More quota**: $20 monthly credit included

## 🔧 What Our App Does to Handle Rate Limits

✅ **Automatic Retry**: Waits 1s, 2s, 4s between retries  
✅ **Smart Error Messages**: Clear feedback about rate limits  
✅ **Graceful Degradation**: App continues working for other features  

## 💡 Tips to Manage Rate Limits

### **1. Check Your Usage**
Visit: https://platform.openai.com/usage
- See current usage
- Monitor remaining quota
- Track API calls

### **2. Optimize Usage**
- **Short audio clips**: Break long recordings into smaller pieces
- **Batch operations**: Don't spam the TTS buttons
- **Text length**: Keep TTS text under 500 characters

### **3. Upgrade If Needed**
- **Heavy usage**: Consider upgrading to Pay-as-you-go
- **Production use**: Plus plan recommended
- **Enterprise**: Contact OpenAI for custom limits

### **4. Alternative Approaches**
- **Wait periods**: Space out audio processing
- **Local models**: Consider offline alternatives for development
- **Caching**: We could add audio caching (future feature)

## 🔍 How to Check Your API Status

1. Go to: https://platform.openai.com/account/usage
2. Check:
   - Current month usage
   - Rate limit status
   - Remaining quota
3. Upgrade plan if needed

## ⚠️ Common Rate Limit Scenarios

| Error | Cause | Solution |
|-------|-------|----------|
| 429 on first use | No quota left | Check usage, add credits |
| 429 after multiple uses | Rate limit hit | Wait 1-2 minutes |
| 429 consistently | Need higher tier | Upgrade plan |

## 📱 Using the App Efficiently

### **STT (Speech-to-Text)**
- Keep audio under 30 seconds
- Wait between uploads if you get 429
- Use clear audio for better results

### **TTS (Text-to-Speech)**
- Don't click speak buttons rapidly
- Shorter text = faster processing
- Wait if you get rate limit errors

## 🎯 Quick Fixes

**If you hit rate limits:**
1. **Wait 2-3 minutes** before trying again
2. **Check OpenAI usage** at platform.openai.com
3. **Add credits** if quota is exhausted
4. **Upgrade plan** for higher limits

Your AI Translator will work great once rate limits are managed! 🚀 