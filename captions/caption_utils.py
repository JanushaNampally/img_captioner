'''

from PIL import Image
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch

# Load pre-trained model and supporting processors
model = VisionEncoderDecoderModel.from_pretrained('nlpconnect/vit-gpt2-image-captioning')
processor = ViTImageProcessor.from_pretrained('nlpconnect/vit-gpt2-image-captioning')
tokenizer = AutoTokenizer.from_pretrained('nlpconnect/vit-gpt2-image-captioning')

def generate_caption(image_path):
    image = Image.open(image_path)
    if image.mode != "RGB":
        image = image.convert(mode="RGB")
    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    output_ids = model.generate(pixel_values, max_length=16, num_beams=4)
    caption = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return caption

# caption_utils.py
def generate_captions(image_path, num_captions=5):
    image = Image.open(image_path)
    if image.mode != "RGB":
        image = image.convert(mode="RGB")

    pixel_values = processor(images=image, return_tensors="pt").pixel_values

    # Beam search and sampling for diversity
    output_ids = model.generate(
        pixel_values,
        max_length=20,
        num_beams=5,
        num_return_sequences=num_captions,
        temperature=1.0,
        top_k=50
    )

    captions = [tokenizer.decode(ids, skip_special_tokens=True) for ids in output_ids]
    return list(set(captions))  # remove duplicates



'''

from PIL import Image
from transformers import VisionEncoderDecoderModel, ViTImageProcessor, AutoTokenizer
import torch
from gtts import gTTS
import os
from googletrans import Translator


# Load pre-trained model and supporting processors
model = VisionEncoderDecoderModel.from_pretrained('nlpconnect/vit-gpt2-image-captioning')
processor = ViTImageProcessor.from_pretrained('nlpconnect/vit-gpt2-image-captioning')
tokenizer = AutoTokenizer.from_pretrained('nlpconnect/vit-gpt2-image-captioning')

# Generate multiple captions
def generate_captions(image_path, num_captions=5):
    image = Image.open(image_path)
    if image.mode != "RGB":
        image = image.convert(mode="RGB")

    pixel_values = processor(images=image, return_tensors="pt").pixel_values

    output_ids = model.generate(
        pixel_values,
        max_length=20,
        num_beams=5,
        num_return_sequences=num_captions,
        temperature=1.0,
        top_k=50
    )

    captions = [tokenizer.decode(ids, skip_special_tokens=True) for ids in output_ids]
    return list(set(captions))  # remove duplicates

# Text-to-speech
def text_to_speech(caption, filename="caption.mp3"):
    tts = gTTS(text=caption, lang='en')
    path = os.path.join("media", filename)
    tts.save(path)
    return path

# Translate captions to multiple languages
translator = Translator()
def translate_caption(caption):
    languages = ['hi', 'te', 'de', ]  # Hindi, Telugu, German, French
    translations = {}
    for lang in languages:
        translations[lang] = translator.translate(caption, dest=lang).text
    return translations

# Evaluate captions with BLEU & METEOR

