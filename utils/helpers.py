"""
Helper utility functions for the Flask application
"""
import re
import secrets
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash


def validate_email(email):
    """
    Validate email format
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password):
    """
    Validate password strength
    
    Requirements:
    - Minimum 8 characters
    - At least one letter
    - At least one number
    
    Args:
        password (str): Password to validate
        
    Returns:
        tuple: (is_valid: bool, error_message: str)
    """
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[a-zA-Z]', password):
        return False, "Password must contain at least one letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    return True, ""


def sanitize_username(username):
    """
    Sanitize username - remove special characters, keep only alphanumeric and dots/underscores
    
    Args:
        username (str): Username to sanitize
        
    Returns:
        str: Sanitized username
    """
    if not username:
        return ""
    # Keep only alphanumeric, dots, underscores, and hyphens
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '', username)
    return sanitized.lower().strip()


def get_user_display_name(user):
    """
    Extract display name from user object (handles all user types)
    
    Args:
        user: User model instance
        
    Returns:
        dict: Dictionary with first_name, last_name, full_name
    """
    first_name = ''
    last_name = ''
    
    if hasattr(user, 'student_profile') and user.student_profile:
        first_name = user.student_profile.first_name or ''
        last_name = user.student_profile.last_name or ''
    elif hasattr(user, 'teacher_profile') and user.teacher_profile:
        first_name = user.teacher_profile.first_name or ''
        last_name = user.teacher_profile.last_name or ''
    else:
        # Fallback: try to extract from username
        parts = (user.username or '').split('.')
        first_name = parts[0].capitalize() if parts and parts[0] else user.username or ''
        last_name = parts[1].capitalize() if len(parts) > 1 else ''
    
    full_name = f"{first_name} {last_name}".strip() or user.username or 'Unknown'
    
    return {
        'first_name': first_name,
        'last_name': last_name,
        'full_name': full_name
    }


def generate_secure_filename(original_filename):
    """
    Generate a secure, unique filename for uploads
    
    Args:
        original_filename (str): Original filename
        
    Returns:
        str: Secure filename with random prefix
    """
    if not original_filename:
        return None
    
    # Get file extension
    ext = os.path.splitext(original_filename)[1]
    
    # Generate random prefix
    random_prefix = secrets.token_urlsafe(16)
    
    # Secure the original filename
    safe_name = secure_filename(original_filename)
    base_name = os.path.splitext(safe_name)[0]
    
    # Combine: random_prefix_timestamp_originalname.ext
    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    new_filename = f"{random_prefix}_{timestamp}_{base_name}{ext}"
    
    return new_filename


def validate_file_extension(filename, allowed_extensions):
    """
    Validate file extension
    
    Args:
        filename (str): Filename to check
        allowed_extensions (set): Set of allowed extensions (without dot)
        
    Returns:
        bool: True if extension is allowed
    """
    if not filename or '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in allowed_extensions


def validate_file_mime_type(file, allowed_mime_types):
    """
    Validate file MIME type (basic check)
    
    Args:
        file: FileStorage object from Flask
        allowed_mime_types (list): List of allowed MIME types
        
    Returns:
        bool: True if MIME type is allowed
    """
    if not file or not file.content_type:
        return False
    
    return file.content_type in allowed_mime_types


def format_datetime(dt, format_str='%b %d, %Y'):
    """
    Format datetime object to string
    
    Args:
        dt: datetime object
        format_str: Format string
        
    Returns:
        str: Formatted datetime string or 'N/A' if None
    """
    if not dt:
        return 'N/A'
    try:
        return dt.strftime(format_str)
    except (AttributeError, ValueError):
        return 'N/A'

