from transformers import DonutProcessor, VisionEncoderDecoderModel, pipeline
from PIL import Image
from gtts import gTTS
from googletrans import Translator
import torch, os


# -----------------------------------------------------------
# 1️⃣ Use Donut (better for screenshots, receipts, UI images)
# -----------------------------------------------------------
processor = DonutProcessor.from_pretrained("naver-clova-ix/donut-base-finetuned-docvqa")
model = VisionEncoderDecoderModel.from_pretrained("naver-clova-ix/donut-base-finetuned-docvqa")
translator = Translator()

# Text summarizer (for paragraph)
summarizer = pipeline("summarization", model="t5-small")

# Creative story generator
story_generator = pipeline("text2text-generation", model="google/flan-t5-base")


# -----------------------------------------------------------
# 2️⃣ Caption Generator (OCR-aware)
# -----------------------------------------------------------
def generate_captions(image_path, num_captions=1):
    """Generate readable caption(s) describing visible text."""
    image = Image.open(image_path).convert("RGB")

    pixel_values = processor(image, return_tensors="pt").pixel_values
    outputs = model.generate(pixel_values, max_length=256)

    text = processor.batch_decode(outputs, skip_special_tokens=True)[0]
    text = text.replace("<s>", "").replace("</s>", "").strip()

    if not text:
        text = "No visible text detected in the image."

    # Return multiple identical captions just to maintain format
    return [text] * num_captions


# -----------------------------------------------------------
# 3️⃣ Summarize multiple captions into a short paragraph
# -----------------------------------------------------------
def generate_paragraph(captions):
    if not captions:
        return "No captions available to summarize."
    combined = " ".join(captions)
    summary = summarizer(combined, max_length=60, min_length=20, do_sample=False)
    return summary[0]["summary_text"]


# -----------------------------------------------------------
# 4️⃣ Translate the text into Hindi, Telugu, German
# -----------------------------------------------------------
def translate_caption(caption):
    languages = {"hi": "Hindi", "te": "Telugu", "de": "German"}
    translations = {}
    for code, name in languages.items():
        try:
            translations[name] = translator.translate(caption, dest=code).text
        except Exception as e:
            translations[name] = f"Translation failed: {e}"
    return translations


# -----------------------------------------------------------
# 5️⃣ Text-to-Speech: store in MEDIA/audio
# -----------------------------------------------------------
def text_to_speech(text, lang_code, filename):
    from django.conf import settings
    audio_dir = os.path.join(settings.MEDIA_ROOT, "audio")
    os.makedirs(audio_dir, exist_ok=True)
    audio_path = os.path.join(audio_dir, f"{filename}_{lang_code}.mp3")

    try:
        if not text.strip():
            print(f"⚠️ Empty text for {lang_code}, skipping TTS")
            return None

        tts = gTTS(text=text, lang=lang_code)
        tts.save(audio_path)
        return f"{settings.MEDIA_URL}audio/{filename}_{lang_code}.mp3"

    except Exception as e:
        print(f"❌ TTS generation failed for {lang_code}: {e}")
        return None


# -----------------------------------------------------------
# 6️⃣ Story generator — contextual and short
# -----------------------------------------------------------
def generate_story(caption):
    if not caption or not isinstance(caption, str):
        return "No caption available for story generation."

    prompt = f"{caption}\nWrite a short creative story about this scene."

    try:
        output = story_generator(
            prompt,
            max_length=120,
            num_return_sequences=1,
            do_sample=True,
            top_p=0.9,
            temperature=0.8,
        )
        story = output[0].get("generated_text", "").strip()

        # Clean redundant bits
        for bad in [prompt, caption, "Write a short creative story about this scene."]:
            story = story.replace(bad, "").strip()

        sentences = []
        for s in story.split(". "):
            if s not in sentences:
                sentences.append(s)
        story = ". ".join(sentences).strip()

        if story:
            story = story[0].upper() + story[1:]
        else:
            story = "Story generation failed."

        return story

    except Exception as e:
        print(f"❌ Story generation failed: {e}")
        return "Error generating story."
