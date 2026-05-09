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
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('api-docs/', views.api_docs, name='api_docs'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
]
