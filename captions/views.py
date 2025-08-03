

# Create your views here.
# captions/views.py

from django.shortcuts import render
from .forms import ImageUploadForm
from .caption_utils import generate_caption
from .models import UploadedImage

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
