

from django.urls import path
from . import views

urlpatterns = [
   # path("", views.home, name="home"),
    path('', views.dashboard, name='dashboard'),
    path('upload/', views.upload_image, name='upload_image'),
    path('paragraph/', views.paragraph_generator, name='paragraph_generator'),
    path('story/', views.story_generator, name='story_generator'),
    path('about/', views.about, name='about'),
]
