'''

# Create your views here.
# captions/views.py

from django.shortcuts import render
from .forms import ImageUploadForm
from .caption_utils import generate_caption
from .models import UploadedImage
from .caption_utils import generate_captions
from gtts import gTTS
import os

def text_to_speech(caption, filename="caption.mp3"):
    tts = gTTS(text=caption, lang='en')
    path = os.path.join("media", filename)
    tts.save(path)
    return path

def image_upload(request):
    captions = None
    img_obj = None
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save()
            # Multiple captions
            captions = generate_captions(img.image.path, num_captions=5)
            img.caption = captions[0]  # store best one in DB
            img.save()
            img_obj = img
    else:
        form = ImageUploadForm()
    return render(request, 'upload.html', {
        'form': form, 'captions': captions, 'img_obj': img_obj
    })

def image_upload(request):
    caption = None
    img_obj = None
    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save()
            # Computer Vision: Generate caption!
            caption = generate_caption(img.image.path)
            img.caption = caption
            img.save()
            img_obj = img
    else:
        form = ImageUploadForm()
    return render(request, 'upload.html', {
        'form': form, 'caption': caption, 'img_obj': img_obj
    })
'''
from django.shortcuts import render
from .forms import ImageUploadForm
from .caption_utils import generate_captions, text_to_speech, translate_caption
from .models import UploadedImage

def image_upload(request):
    captions = None
    translations = None
    img_obj = None
    audio_path = None
    

    if request.method == "POST":
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            img = form.save()

            # Generate multiple captions
            captions = generate_captions(img.image.path, num_captions=5)
            img.caption = captions[0]  # store the first one in DB
            img.save()
            img_obj = img

            # Convert best caption to audio
            audio_path = text_to_speech(captions[0], "caption.mp3")

            # Translate best caption
            translations = translate_caption(captions[0])

            # Dummy evaluation: using first caption as reference, second as hypothesis
           

    else:
        form = ImageUploadForm()

    return render(request, 'upload.html', {
        'form': form,
        'captions': captions,
        'img_obj': img_obj,
        'audio_path': audio_path,
        'translations': translations
        
    })


