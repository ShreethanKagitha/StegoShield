"""
Forms for the Steganography Application
"""

from django import forms


class EncodeForm(forms.Form):
    """Form for encoding a message into an image."""
    
    image = forms.ImageField(
        label='Select Image',
        help_text='Upload a PNG or BMP image (max 10MB)',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/png,image/bmp',
            'id': 'encode-image-input'
        })
    )
    
    message = forms.CharField(
        label='Secret Message',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Enter your secret message here...',
            'id': 'secret-message'
        }),
        max_length=100000,
        help_text='Your message will be hidden in the image'
    )
    
    use_qr_code = forms.BooleanField(
        label='Use QR Code',
        required=False,
        help_text='Convert message to QR code before embedding (increases robustness)',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'use-qr'
        })
    )

    password = forms.CharField(
        label='Encryption Password (Optional)',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password to encrypt message',
            'id': 'encode-password'
        }),
        help_text='If provided, message will be encrypted with AES-256'
    )


class DecodeForm(forms.Form):
    """Form for decoding a message from a stego-image."""
    
    image = forms.ImageField(
        label='Select Stego-Image',
        help_text='Upload the image containing a hidden message',
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': 'image/png,image/bmp',
            'id': 'decode-image-input'
        })
    )

    password = forms.CharField(
        label='Decryption Password (If encrypted)',
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter password if message is encrypted',
            'id': 'decode-password'
        })
    )
