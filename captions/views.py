# captions/views.py
from django.shortcuts import render
from .caption_utils import generate_captions, translate_caption, text_to_speech, generate_paragraph, generate_story
from googletrans import Translator
import os
from gtts import gTTS


def dashboard(request):
    return render(request, 'captions/dashboard.html')

def paragraph_generator(request):
    return render(request, 'captions/paragraph.html')
def story_generator(request):
    return render(request, 'captions/story.html')
def about(request):
    return render(request, 'captions/about.html')

def upload_image(request):
    context = {}

    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]

        # Save uploaded image
        upload_dir = "captions/static/captions/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        image_path = os.path.join(upload_dir, image.name)
        with open(image_path, "wb+") as dest:
            for chunk in image.chunks():
                dest.write(chunk)

        # 1️⃣ Generate English captions
        captions = generate_captions(image_path)
        best_caption = captions[0] if captions else "No caption generated."

        # 2️⃣ Translate into Hindi, Telugu, German
        translations = translate_caption(best_caption)

        # 3️⃣ Generate audio (English + Translations)
        langs = {'English': 'en', 'Hindi': 'hi', 'Telugu': 'te', 'German': 'de'}
        audio_files = {}
        filename = os.path.splitext(image.name)[0]

        for lang_name, lang_code in langs.items():
            text = best_caption if lang_name == "English" else translations.get(lang_name, "")
            audio_files[lang_name] = text_to_speech(text, lang_code, filename)

        # 4️⃣ Generate paragraph and story
        paragraph = generate_paragraph(captions)
        story = generate_story(str(best_caption))

        # 5️⃣ Send all data to template
        context = {
            "image_path": f"static/captions/uploads/{image.name}",
            "captions": captions,
            "best_caption": best_caption,
            "translations": translations,
            "audio_files": audio_files,
            "paragraph": paragraph,
            "story": story,
        }

    # Always render the upload page (with or without results)
    return render(request, "captions/upload.html", context)
