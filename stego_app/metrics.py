"""
Image Quality Metrics for Steganography Analysis
Calculates MSE, PSNR and generates histogram data.
"""

import numpy as np
from PIL import Image
import math

def calculate_mse(image1, image2):
    """
    Calculate Mean Squared Error between two images.
    
    Args:
        image1: First PIL Image
        image2: Second PIL Image
        
    Returns:
        float: MSE value
    """
    # Convert images to numpy arrays
    img1 = np.array(image1).astype(np.float64)
    img2 = np.array(image2).astype(np.float64)
    
    # Calculate MSE
    err = np.sum((img1 - img2) ** 2)
    err /= float(img1.shape[0] * img1.shape[1] * img1.shape[2])
    
    return err

def calculate_psnr(image1, image2):
    """
    Calculate Peak Signal-to-Noise Ratio between two images.
    
    Args:
        image1: First PIL Image
        image2: Second PIL Image
        
    Returns:
        float: PSNR value in dB
    """
    mse = calculate_mse(image1, image2)
    
    # If MSE is zero, images are identical
    if mse == 0:
        return 100.0
    
    # max_pixel is 255 for 8-bit images
    max_pixel = 255.0
    psnr = 20 * math.log10(max_pixel / math.sqrt(mse))
    
    return psnr

def generate_histogram_data(image):
    """
    Generate RGB histogram data for an image.
    
    Args:
        image: PIL Image
        
    Returns:
        dict: containing lists for r, g, b channels
    """
    # Ensure image is RGB
    if image.mode != 'RGB':
        image = image.convert('RGB')
        
    # Get histogram
    # Returns a list of 768 integers (256 red, 256 green, 256 blue)
    histogram = image.histogram()
    
    return {
        'r': histogram[0:256],
        'g': histogram[256:512],
        'b': histogram[512:768]
    }

def compare_images(original_img, stego_img):
    """
    Perform comprehensive comparison between original and stego images.
    
    Args:
        original_img: Original PIL Image
        stego_img: Stego PIL Image
        
    Returns:
        dict: metrics including mse, psnr, and histograms
    """
    mse = calculate_mse(original_img, stego_img)
    psnr = calculate_psnr(original_img, stego_img)
    
    hist_original = generate_histogram_data(original_img)
    hist_stego = generate_histogram_data(stego_img)
    
    return {
        'mse': round(mse, 6),
        'psnr': round(psnr, 2),
        'hist_original': hist_original,
        'hist_stego': hist_stego
    }
