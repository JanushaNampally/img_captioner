import os
from pathlib import Path
from PIL import Image
from gtts import gTTS
from googletrans import Translator

import torch
from transformers import (
    VisionEncoderDecoderModel,
    ViTImageProcessor,
    AutoTokenizer,
    pipeline,
)

# ----------- Model & utils (load once) -----------
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

caption_model = VisionEncoderDecoderModel.from_pretrained(
    "nlpconnect/vit-gpt2-image-captioning"
).to(DEVICE)
caption_feature_extractor = ViTImageProcessor.from_pretrained(
    "nlpconnect/vit-gpt2-image-captioning"
)
caption_tokenizer = AutoTokenizer.from_pretrained(
    "nlpconnect/vit-gpt2-image-captioning"
)

# lightweight text pipelines
summarizer = pipeline("summarization", model="t5-small")
story_generator = pipeline("text2text-generation", model="google/flan-t5-base")
translator = Translator()


# ----------- Caption generator -----------
def generate_captions(image_path: str, num_captions: int = 1):
    """
    Returns a list of `num_captions` captions for the given image_path.
    Uses nlpconnect/vit-gpt2-image-captioning.
    """
    image = Image.open(image_path).convert("RGB")

    # ensure consistent tensor shapes (padding)
    inputs = caption_feature_extractor(
        images=image, return_tensors="pt", padding="max_length"
    )
    pixel_values = inputs.pixel_values.to(DEVICE)

    # generate
    output_ids = caption_model.generate(
        pixel_values,
        max_length=50,
        num_beams=4,
        no_repeat_ngram_size=2,
        early_stopping=True,
    )

    caption = caption_tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()

    if not caption:
        caption = "No caption generated."

    # Return list (repeat if user asked for multiple; can be improved later)
    return [caption] * max(1, num_captions)


# ----------- Paragraph summarizer -----------
def generate_paragraph(captions):
    if not captions:
        return "No captions available to summarize."

    combined = " ".join(captions)
    summary = summarizer(combined, max_length=80, min_length=25, do_sample=False)
    return summary[0]["summary_text"]


# ----------- Translate caption -----------
def translate_caption(caption: str):
    languages = {"hi": "Hindi", "te": "Telugu", "de": "German"}
    translations = {}
    for code, name in languages.items():
        try:
            translations[name] = translator.translate(caption, dest=code).text
        except Exception as e:
            translations[name] = f"Translation failed: {e}"
    return translations


# ----------- Text to speech -----------
def text_to_speech(text: str, lang_code: str, filename: str):
    """
    Saves mp3 in MEDIA_ROOT/audio and returns MEDIA_URL path or None.
    """
    if not text or not text.strip():
        return None

    from django.conf import settings

    audio_dir = Path(settings.MEDIA_ROOT) / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    audio_path = audio_dir / f"{filename}_{lang_code}.mp3"
    try:
        tts = gTTS(text=text, lang=lang_code)
        tts.save(str(audio_path))
        return f"{settings.MEDIA_URL}audio/{filename}_{lang_code}.mp3"
    except Exception as e:
        # keep server from crashing; log and return None
        print(f"TTS failed for {lang_code}: {e}")
        return None


# ----------- Story generator -----------
def generate_story(caption: str):
    if not caption or not isinstance(caption, str):
        return "No caption available for story generation."

    prompt = f"{caption}\nWrite a short creative story about this scene."
    try:
        output = story_generator(
            prompt,
            max_length=150,
            num_return_sequences=1,
            do_sample=True,
            top_p=0.9,
            temperature=0.8,
        )
        story = output[0].get("generated_text", "").replace(prompt, "").strip()
        return story if story else "Story generation failed."
    except Exception as e:
        print(f"Story generation failed: {e}")
        return "Error generating story."
