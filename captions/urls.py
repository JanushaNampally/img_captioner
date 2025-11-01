

from django.urls import path
from . import views

urlpatterns = [
    path('', views.upload_image, name='upload_image'),   # your home/upload page
    path('about/', views.about, name='about'),           # ✅ new About page
]
