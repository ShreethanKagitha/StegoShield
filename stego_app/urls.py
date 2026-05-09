"""
URL configuration for stego_app
"""

from django.urls import path
from . import views

app_name = 'stego_app'

urlpatterns = [
    path('', views.home, name='home'),
    path('encode/', views.encode, name='encode'),
    path('decode/', views.decode, name='decode'),
    path('api/capacity/', views.calculate_image_capacity, name='calculate_capacity'),
    path('download/', views.download_stego_image, name='download'),
    path('dashboard/', views.dashboard, name='dashboard'),
]
