"""
Integrity Verification Utilities
Implements message hashing and verification for tamper detection.
"""

import hashlib

# Marker for integrity header
INTEGRITY_MARKER = "<<INT>>"
HASH_LENGTH = 64  # SHA-256 hex digest length

def generate_hash(data):
    """
    Generate SHA-256 hash of the data.
    
    Args:
        data (str): Input data
        
    Returns:
        str: 64-character hex digest
    """
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def add_integrity(message):
    """
    Add integrity header with hash to the message.
    
    Args:
        message (str): Original message
        
    Returns:
        str: Message with integrity header (<<INT>>HASH+MESSAGE)
    """
    msg_hash = generate_hash(message)
    return f"{INTEGRITY_MARKER}{msg_hash}{message}"

def verify_integrity(content):
    """
    Verify integrity of content containing a hash header.
    
    Args:
        content (str): Content with integrity header
        
    Returns:
        tuple: (verified (bool), original_message (str))
    """
    if not content.startswith(INTEGRITY_MARKER):
        return None, content  # No integrity header found
        
    try:
        # Extract hash and message
        # Format: <<INT>>[64 chars hash][message]
        header_len = len(INTEGRITY_MARKER)
        extracted_hash = content[header_len:header_len + HASH_LENGTH]
        original_message = content[header_len + HASH_LENGTH:]
        
        # Calculate expected hash
        calculated_hash = generate_hash(original_message)
        
        # Verify
        is_verified = (extracted_hash == calculated_hash)
        
        return is_verified, original_message
        
    except Exception:
        return False, content
