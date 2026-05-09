"""
Views for the Steganography Application
"""

from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
import base64
from PIL import Image
import io

from .forms import EncodeForm, DecodeForm
from .utils import encode_message, decode_message, calculate_capacity, validate_image
from .models import StegoStats
import time
from django.db.models import Avg, Count
from django.utils import timezone


def home(request):
    """Home page with feature overview."""
    return render(request, 'stego_app/home.html')


def encode(request):
    """Handle image encoding - hide a message in an image."""
    context = {
        'form': EncodeForm(),
        'encoded_image': None,
        'error': None,
        'capacity_info': None
    }
    
    if request.method == 'POST':
        form = EncodeForm(request.POST, request.FILES)
        
        if form.is_valid():
            start_time = time.time()
            try:
                image_file = request.FILES['image']
                # Get file size
                image_size = image_file.size
                
                message = form.cleaned_data['message']
                password = form.cleaned_data['password']
                use_qr = form.cleaned_data['use_qr_code']
                
                # Validate image format
                is_valid, error_msg = validate_image(image_file)
                if not is_valid:
                    context['error'] = error_msg
                    context['form'] = form
                    return render(request, 'stego_app/encode.html', context)
                
                # Calculate capacity
                image_file.seek(0)
                try:
                    capacity = calculate_capacity(image_file)
                    context['capacity_info'] = capacity
                    
                    # Check if message fits
                    if len(message) > capacity['max_chars']:
                        context['error'] = f"Message too long! Maximum {capacity['max_chars']} characters allowed."
                        context['form'] = form
                        return render(request, 'stego_app/encode.html', context)
                    
                    # Encode the message
                    image_file.seek(0)
                    encoded_data = encode_message(image_file, message, password, use_qr)
                    
                    # Calculate metrics (PSNR, MSE, Histograms)
                    from .metrics import compare_images
                    
                    # Re-open original image for comparison
                    image_file.seek(0)
                    original_img = Image.open(image_file).convert('RGB')
                    
                    # Open stego image from bytes
                    stego_img = Image.open(io.BytesIO(encoded_data)).convert('RGB')
                    
                    # Get metrics
                    metrics = compare_images(original_img, stego_img)
                    context['metrics'] = metrics
                    
                    # Convert to base64 for download
                    encoded_b64 = base64.b64encode(encoded_data).decode('utf-8')
                    context['encoded_image'] = encoded_b64
                    context['success'] = True
                    context['message_length'] = len(message)
                    
                    # Record Stats
                    processing_time = (time.time() - start_time) * 1000
                    StegoStats.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        operation='ENCODE',
                        image_size_bytes=image_size,
                        message_length=len(message),
                        psnr=metrics['psnr'],
                        mse=metrics['mse'],
                        processing_time_ms=processing_time,
                        success=True
                    )
                    
                except Exception as e:
                    context['error'] = str(e)
                    # Record Failure
                    processing_time = (time.time() - start_time) * 1000
                    StegoStats.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        operation='ENCODE',
                        image_size_bytes=image_size,
                        message_length=len(message),
                        processing_time_ms=processing_time,
                        success=False
                    )

            except Exception as e:
                context['error'] = str(e)
        else:
            context['error'] = 'Please correct the errors below.'
        
        context['form'] = form
    
    return render(request, 'stego_app/encode.html', context)


def decode(request):
    """Handle image decoding - extract hidden message from image."""
    context = {
        'form': DecodeForm(),
        'decoded_message': None,
        'error': None
    }
    
    if request.method == 'POST':
        form = DecodeForm(request.POST, request.FILES)
        
        if form.is_valid():
            start_time = time.time()
            image_file = request.FILES['image']
            password = form.cleaned_data['password']
            image_size = image_file.size
            
            try:
                # Decode the message
                message, is_verified = decode_message(image_file, password)
                context['decoded_message'] = message
                context['integrity_verified'] = is_verified
                context['success'] = True
                
                # Record Stats
                processing_time = (time.time() - start_time) * 1000
                StegoStats.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    operation='DECODE',
                    image_size_bytes=image_size,
                    message_length=len(message) if message else 0,
                    processing_time_ms=processing_time,
                    success=True
                )
                
            except Exception as e:
                context['error'] = str(e)
                # Record Failure
                processing_time = (time.time() - start_time) * 1000
                StegoStats.objects.create(
                    user=request.user if request.user.is_authenticated else None,
                    operation='DECODE',
                    image_size_bytes=image_size,
                    processing_time_ms=processing_time,
                    success=False
                )
        else:
            context['error'] = 'Please select a valid image file.'
        
        context['form'] = form
    
    return render(request, 'stego_app/decode.html', context)


@require_http_methods(["POST"])
def calculate_image_capacity(request):
    """API endpoint to calculate image capacity."""
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image provided'}, status=400)
        
        image_file = request.FILES['image']
        
        # Validate image
        is_valid, error_msg = validate_image(image_file)
        if not is_valid:
            return JsonResponse({'error': error_msg}, status=400)
        
        # Calculate capacity
        image_file.seek(0)
        capacity = calculate_capacity(image_file)
        
        return JsonResponse({
            'success': True,
            'capacity': capacity
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def download_stego_image(request):
    """Download the encoded stego-image."""
    if request.method == 'POST':
        image_data = request.POST.get('image_data')
        if image_data:
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            
            # Create response
            response = HttpResponse(image_bytes, content_type='image/png')
            response['Content-Disposition'] = 'attachment; filename="stego_image.png"'
            return response
    
    return HttpResponse('No image data provided', status=400)


@login_required
def dashboard(request):
    """
    Performance analysis dashboard view.
    """
    # Aggregate stats for the current user
    user_stats = StegoStats.objects.filter(user=request.user)
    
    total_ops = user_stats.count()
    encode_ops = user_stats.filter(operation='ENCODE').count()
    decode_ops = user_stats.filter(operation='DECODE').count()
    
    avg_psnr = user_stats.filter(operation='ENCODE', psnr__isnull=False).aggregate(Avg('psnr'))['psnr__avg']
    avg_time = user_stats.aggregate(Avg('processing_time_ms'))['processing_time_ms__avg']
    
    recent_activity = user_stats.all()[:10]
    
    context = {
        'total_ops': total_ops,
        'encode_ops': encode_ops,
        'decode_ops': decode_ops,
        'avg_psnr': round(avg_psnr, 2) if avg_psnr else 0,
        'avg_time': round(avg_time, 2) if avg_time else 0,
        'recent_activity': recent_activity
    }
    return render(request, 'stego_app/dashboard.html', context)


def how_it_works(request):
    """How it works information page."""
    return render(request, 'stego_app/how_it_works.html')


def api_docs(request):
    """API documentation page."""
    return render(request, 'stego_app/api_docs.html')


def privacy(request):
    """Privacy policy page."""
    return render(request, 'stego_app/privacy.html')


def terms(request):
    """Terms of service page."""
    return render(request, 'stego_app/terms.html')


def user_login(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('stego_app:home')
        
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            auth_login(request, user)
            return redirect('stego_app:home')
        else:
            messages.error(request, 'Invalid clearance credentials.')
            
    return render(request, 'stego_app/login.html')

def user_register(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('stego_app:home')
        
    if request.method == 'POST':
        u = request.POST.get('username')
        p1 = request.POST.get('password')
        p2 = request.POST.get('password_confirm')
        
        if User.objects.filter(username=u).exists():
            messages.error(request, 'Identity already exists in the system.')
        elif p1 != p2:
            messages.error(request, 'Passphrases do not match.')
        else:
            user = User.objects.create_user(username=u, password=p1)
            auth_login(request, user)
            return redirect('stego_app:home')
            
    return render(request, 'stego_app/register.html')

def user_logout(request):
    """Handle user logout."""
    auth_logout(request)
    return redirect('stego_app:login')
