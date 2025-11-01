# captions/caption_utils.py
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
from gtts import gTTS
from googletrans import Translator
import torch
import os

# Load BLIP model once (fast + accurate)
processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
translator = Translator()

def generate_captions(image_path, num_captions=4):
    """Generate up to 4 diverse English captions for the given image."""
    image = Image.open(image_path).convert("RGB")
    inputs = processor(image, return_tensors="pt")

    captions = []
    for _ in range(num_captions * 2):  # generate more and pick unique
        output = model.generate(**inputs, max_length=30, num_beams=5, temperature=1.0, top_p=0.9)
        caption = processor.decode(output[0], skip_special_tokens=True).strip().capitalize()
        if caption not in captions:
            captions.append(caption)
        if len(captions) >= num_captions:
            break
    return captions


def translate_caption(caption):
    """Translate best caption into Hindi, Telugu, and German."""
    languages = {
        'hi': 'Hindi',
        'te': 'Telugu',
        'de': 'German',
    }
    translations = {}
    for code, name in languages.items():
        try:
            translated_text = translator.translate(caption, dest=code).text
            translations[name] = translated_text
        except Exception as e:
            translations[name] = f"Translation failed: {e}"
    return translations


def text_to_speech(text, lang_code, filename):
    """Convert text to speech and save as MP3 for each language."""
    audio_dir = "captions/static/captions/audio"
    os.makedirs(audio_dir, exist_ok=True)
    path = f"{audio_dir}/{filename}_{lang_code}.mp3"
    try:
        tts = gTTS(text=text, lang=lang_code)
        tts.save(path)
        return f"/static/captions/audio/{filename}_{lang_code}.mp3"
    except Exception as e:
        print(f"TTS generation failed for {lang_code}: {e}")
        return None
