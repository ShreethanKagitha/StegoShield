"""
Crypto Utilities for Secure Data Hiding
Implements AES-256 encryption/decryption and key derivation.
"""

from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64

# Constants
SALT_SIZE = 16
IV_SIZE = 16
KEY_SIZE = 32  # 256 bits
ITERATIONS = 100000

def derive_key(password, salt):
    """
    Derive a 256-bit key from the password using PBKDF2.
    
    Args:
        password (str): The secret password
        salt (bytes): Random salt
        
    Returns:
        bytes: The derived 32-byte key
    """
    return PBKDF2(password, salt, dkLen=KEY_SIZE, count=ITERATIONS)

def encrypt_data(data, password):
    """
    Encrypt string data using AES-256-CBC.
    
    Args:
        data (str): The message to encrypt
        password (str): The encryption password
        
    Returns:
        str: Base64 encoded encrypted string containing salt, iv, and ciphertext
    """
    try:
        # Generate random salt
        salt = get_random_bytes(SALT_SIZE)
        
        # Derive key
        key = derive_key(password, salt)
        
        # Generate random IV
        iv = get_random_bytes(IV_SIZE)
        
        # Create cipher
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Pad and encrypt
        padded_data = pad(data.encode('utf-8'), AES.block_size)
        ciphertext = cipher.encrypt(padded_data)
        
        # Combine salt + iv + ciphertext
        result = salt + iv + ciphertext
        
        # Return as base64 string
        return base64.b64encode(result).decode('utf-8')
        
    except Exception as e:
        raise ValueError(f"Encryption failed: {str(e)}")

def decrypt_data(encrypted_data_b64, password):
    """
    Decrypt AES-256-CBC encrypted data.
    
    Args:
        encrypted_data_b64 (str): Base64 encoded encrypted string
        password (str): The decryption password
        
    Returns:
        str: Decrypted message
    """
    try:
        # Decode base64
        encrypted_data = base64.b64decode(encrypted_data_b64)
        
        # Extract components
        if len(encrypted_data) < SALT_SIZE + IV_SIZE:
            raise ValueError("Invalid encrypted data format")
            
        salt = encrypted_data[:SALT_SIZE]
        iv = encrypted_data[SALT_SIZE:SALT_SIZE + IV_SIZE]
        ciphertext = encrypted_data[SALT_SIZE + IV_SIZE:]
        
        # Derive key
        key = derive_key(password, salt)
        
        # Create cipher
        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # Decrypt and unpad
        decrypted_padded = cipher.decrypt(ciphertext)
        decrypted_data = unpad(decrypted_padded, AES.block_size)
        
        return decrypted_data.decode('utf-8')
        
    except (ValueError, KeyError) as e:
        raise ValueError("Decryption failed. Incorrect password or corrupted data.")
    except Exception as e:
        raise ValueError(f"Decryption error: {str(e)}")
