"""
LSB Steganography Utilities

This module implements the Least Significant Bit (LSB) steganography technique
for hiding secret messages within images.
"""

from PIL import Image
import io
from .crypto import encrypt_data, decrypt_data
from .integrity import add_integrity, verify_integrity
from .qr_stego import generate_qr_base64, decode_qr_base64, QR_MARKER


# Delimiter to mark end of message
MESSAGE_DELIMITER = "<<END>>"
ENCRYPTION_MARKER = "<<ENC>>"


def calculate_capacity(image_file):
    """
    Calculate the maximum message capacity of an image.
    
    Args:
        image_file: File object or path to the image
        
    Returns:
        dict: Contains 'max_bytes', 'max_chars', 'width', 'height', 'total_pixels'
    """
    try:
        img = Image.open(image_file)
        width, height = img.size
        total_pixels = width * height
        
        # Each pixel has 3 channels (RGB), each can store 1 bit
        # 8 bits = 1 byte/character
        max_bits = total_pixels * 3
        max_bytes = max_bits // 8
        
        # Reserve space for delimiter
        delimiter_size = len(MESSAGE_DELIMITER)
        # Approximate overhead for headers (Integrity + Encryption) ~ 80-100 chars
        overhead = 100
        max_chars = max_bytes - delimiter_size - overhead
        
        return {
            'max_bytes': max_bytes,
            'max_chars': max(0, max_chars),
            'width': width,
            'height': height,
            'total_pixels': total_pixels
        }
    except Exception as e:
        raise ValueError(f"Error calculating capacity: {str(e)}")


def validate_image(image_file):
    """
    Validate that the uploaded file is a valid PNG or BMP image.
    
    Args:
        image_file: File object to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Reset file pointer
        image_file.seek(0)
        
        # Try to open the image
        img = Image.open(image_file)
        
        # Check format
        if img.format not in ['PNG', 'BMP']:
            return False, "Only PNG and BMP images are supported. JPEG uses lossy compression which destroys hidden data."
        
        # Check mode
        if img.mode not in ['RGB', 'RGBA']:
            return False, "Image must be in RGB or RGBA mode."
        
        # Reset file pointer for later use
        image_file.seek(0)
        
        return True, None
        
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"


def text_to_binary(text):
    """Convert text to binary string."""
    return ''.join(format(ord(char), '08b') for char in text)


def binary_to_text(binary_str):
    """Convert binary string to text."""
    chars = []
    for i in range(0, len(binary_str), 8):
        byte = binary_str[i:i+8]
        if len(byte) == 8:
            chars.append(chr(int(byte, 2)))
    return ''.join(chars)


def encode_message(image_file, message, password=None, use_qr=False):
    """
    Encode a secret message into an image using LSB steganography.
    
    Args:
        image_file: File object or path to the cover image
        message: String message to hide
        password: Optional password for encryption
        use_qr: Boolean to use QR code encoding
        
    Returns:
        bytes: PNG image data with hidden message
    """
    try:
        # Open the image
        img = Image.open(image_file)
        
        # Convert to RGB if necessary
        if img.mode == 'RGBA':
            # Create a white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 0. Convert to QR if requested
        if use_qr:
            message = generate_qr_base64(message)
        
        # 1. Encrypt message if password provided
        if password:
            message = ENCRYPTION_MARKER + encrypt_data(message, password)
            
        # 2. Add integrity check
        message = add_integrity(message)
        
        # 3. Add delimiter
        full_message = message + MESSAGE_DELIMITER
        
        # Convert message to binary
        binary_message = text_to_binary(full_message)
        
        # Check capacity
        width, height = img.size
        max_bits = width * height * 3
        
        if len(binary_message) > max_bits:
            raise ValueError(f"Message too long! Maximum capacity: {max_bits // 8} characters")
        
        # Get pixel data
        pixels = list(img.getdata())
        
        # Encode message into pixels
        bit_index = 0
        new_pixels = []
        
        for pixel in pixels:
            r, g, b = pixel[:3]
            
            # Modify Red channel
            if bit_index < len(binary_message):
                r = (r & ~1) | int(binary_message[bit_index])
                bit_index += 1
            
            # Modify Green channel
            if bit_index < len(binary_message):
                g = (g & ~1) | int(binary_message[bit_index])
                bit_index += 1
            
            # Modify Blue channel
            if bit_index < len(binary_message):
                b = (b & ~1) | int(binary_message[bit_index])
                bit_index += 1
            
            new_pixels.append((r, g, b))
        
        # Create new image with encoded data
        encoded_img = Image.new('RGB', img.size)
        encoded_img.putdata(new_pixels)
        
        # Save to bytes
        output = io.BytesIO()
        encoded_img.save(output, format='PNG')
        output.seek(0)
        
        return output.getvalue()
        
    except Exception as e:
        raise ValueError(f"Error encoding message: {str(e)}")


def decode_message(image_file, password=None):
    """
    Extract a hidden message from a stego-image using LSB steganography.
    
    Args:
        image_file: File object or path to the stego-image
        password: Optional password for decryption
        
    Returns:
        tuple: (message, integrity_verified)
    """
    try:
        # Open the image
        img = Image.open(image_file)
        
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Get pixel data
        pixels = list(img.getdata())
        
        # Extract bits from LSB of each channel
        binary_message = ''
        
        for pixel in pixels:
            r, g, b = pixel[:3]
            binary_message += str(r & 1)
            binary_message += str(g & 1)
            binary_message += str(b & 1)
        
        # Convert binary to text
        message = binary_to_text(binary_message)
        
        # Find delimiter
        if MESSAGE_DELIMITER in message:
            message = message.split(MESSAGE_DELIMITER)[0]
            
            # 1. Verify Integrity
            is_verified, message = verify_integrity(message)
            
            # 2. Check for encryption
            decrypted_message = message
            if message.startswith(ENCRYPTION_MARKER):
                if not password:
                    return "🔒 This message is encrypted. Please provide a password to decrypt it.", is_verified
                
                try:
                    encrypted_data = message[len(ENCRYPTION_MARKER):]
                    decrypted_message = decrypt_data(encrypted_data, password)
                except Exception:
                    return "❌ Incorrect password or corrupted data.", False
            elif password:
                return "⚠️ Message was not encrypted, but a password was provided. Message: " + message, is_verified
            
            # 3. Check for QR Code
            if decrypted_message.startswith(QR_MARKER):
                try:
                    decrypted_message = decode_qr_base64(decrypted_message)
                except Exception as e:
                    return f"❌ QR Code detected but could not be decoded: {str(e)}", is_verified
            
            return decrypted_message, is_verified
        else:
            raise ValueError("No hidden message found or message is corrupted.")
            
    except Exception as e:
        raise ValueError(f"Error decoding message: {str(e)}")
