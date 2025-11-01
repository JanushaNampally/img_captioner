# captions/views.py
from django.shortcuts import render
from .caption_utils import generate_captions, translate_caption, text_to_speech
import os
from django.shortcuts import render

def about(request):
    return render(request, 'captions/about.html')

def upload_image(request):
    context = {}
    if request.method == "POST" and "image" in request.FILES:
        image_file = request.FILES["image"]
        upload_dir = "captions/static/captions/uploads"
        os.makedirs(upload_dir, exist_ok=True)

        image_path = f"{upload_dir}/{image_file.name}"
        with open(image_path, "wb+") as dest:
            for chunk in image_file.chunks():
                dest.write(chunk)

        # Generate English captions
        english_captions = generate_captions(image_path)
        best_caption = english_captions[0] if english_captions else "No caption generated."

        # Translate best caption
        translations = translate_caption(best_caption)

        # Generate audio files for English and translations
        langs = {'English': 'en', 'Hindi': 'hi', 'Telugu': 'te', 'German': 'de'}
        audio_files = {}
        for lang_name, lang_code in langs.items():
            text = best_caption if lang_name == "English" else translations.get(lang_name, "")
            filename = os.path.splitext(image_file.name)[0]
            audio_files[lang_name] = text_to_speech(text, lang_code, filename)

        context = {
            "image_url": f"/static/captions/uploads/{image_file.name}",
            "captions_en": english_captions,
            "best_caption": best_caption,
            "translations": translations,
            "audio_files": audio_files,
        }

    return render(request, "captions/upload.html", context)
