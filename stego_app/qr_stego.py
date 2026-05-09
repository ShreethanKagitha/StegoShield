import qrcode
from PIL import Image
import io
import base64

try:
    from pyzbar.pyzbar import decode
    PYZBAR_AVAILABLE = True
except Exception:
    # Catches ImportError, OSError, etc. if zbar lib is missing
    PYZBAR_AVAILABLE = False

QR_MARKER = "<<QR>>"

def generate_qr_base64(message):
    """
    Convert a message into a QR code and return as base64 string.
    
    Args:
        message (str): Message to encode
        
    Returns:
        str: Base64 string of the QR code image (prefixed with marker)
    """
    try:
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(message)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to bytes
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        
        # Encode to base64
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return QR_MARKER + img_str
        
    except Exception as e:
        raise ValueError(f"QR generation failed: {str(e)}")

try:
    import cv2
    import numpy as np
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False

def decode_qr_base64(base64_str):
    """
    Decode a base64 encoded QR code image to get the message.
    
    Args:
        base64_str (str): Base64 encoded QR code (with optional marker)
        
    Returns:
        str: Decoded message from QR code
    """
    if not PYZBAR_AVAILABLE and not CV2_AVAILABLE:
        return "⚠️ QR decoding is not available. System missing 'libzbar' and 'opencv-python'."

    try:
        # Remove marker if present
        if base64_str.startswith(QR_MARKER):
            base64_str = base64_str[len(QR_MARKER):]
            
        # Decode base64
        img_data = base64.b64decode(base64_str)
        img = Image.open(io.BytesIO(img_data))
        
        # Try Pyzbar first (usually faster/more robust for simple codes)
        if PYZBAR_AVAILABLE:
            decoded_objects = decode(img)
            if decoded_objects:
                return decoded_objects[0].data.decode('utf-8')
        
        # Fallback to OpenCV
        if CV2_AVAILABLE:
            # Convert PIL image to OpenCV format
            open_cv_image = np.array(img.convert('RGB')) 
            # Convert RGB to BGR 
            open_cv_image = open_cv_image[:, :, ::-1].copy() 
            
            detector = cv2.QRCodeDetector()
            data, bbox, _ = detector.detectAndDecode(open_cv_image)
            
            if data:
                return data
                
        return "Could not detect QR code in the extracted data."
            
    except Exception as e:
        raise ValueError(f"QR decoding failed: {str(e)}")
