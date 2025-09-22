# detection/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('upload/', views.upload_image_view, name='upload-image'),
    path('live/', views.live_stream_view, name='live-stream'),
    path('video_feed/', views.video_stream, name='video-feed'),
]

