"""Image processing utilities - compression, resize, thumbnails."""
import os
from io import BytesIO
from PIL import Image, ImageOps, ExifTags


# Constants
MAX_IMAGE_SIZE = (1200, 1200)  # Max dimensions for uploaded photos
THUMBNAIL_SIZE = (300, 300)    # Size for thumbnails
JPEG_QUALITY = 85              # Quality for JPEG compression
MAX_FILE_SIZE_MB = 5           # Max file size in MB


def process_uploaded_image(file, output_path, create_thumbnail=True):
    """
    Process an uploaded image:
    - Fix orientation based on EXIF
    - Resize if too large
    - Compress for web
    - Optionally create thumbnail
    
    Returns: (success, error_message, thumbnail_path)
    """
    try:
        # Open image
        img = Image.open(file)
        
        # Fix orientation based on EXIF data
        img = fix_image_orientation(img)
        
        # Convert to RGB if necessary (handles PNG with transparency, etc.)
        if img.mode in ('RGBA', 'P', 'LA'):
            # Create white background for transparent images
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if 'A' in img.mode else None)
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if too large
        img.thumbnail(MAX_IMAGE_SIZE, Image.Resampling.LANCZOS)
        
        # Save compressed image
        img.save(output_path, 'JPEG', quality=JPEG_QUALITY, optimize=True)
        
        # Create thumbnail if requested
        thumbnail_path = None
        if create_thumbnail:
            thumb = img.copy()
            thumb.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            
            # Generate thumbnail path
            base, ext = os.path.splitext(output_path)
            thumbnail_path = f"{base}_thumb.jpg"
            thumb.save(thumbnail_path, 'JPEG', quality=80, optimize=True)
        
        return True, None, thumbnail_path
        
    except Exception as e:
        return False, str(e), None


def fix_image_orientation(img):
    """
    Fix image orientation based on EXIF data.
    Mobile photos often need rotation.
    """
    try:
        # Get EXIF data
        exif = img._getexif()
        if exif is None:
            return img
        
        # Find orientation tag
        orientation_key = None
        for key, val in ExifTags.TAGS.items():
            if val == 'Orientation':
                orientation_key = key
                break
        
        if orientation_key is None or orientation_key not in exif:
            return img
        
        orientation = exif[orientation_key]
        
        # Apply rotation/flip based on orientation
        if orientation == 2:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 3:
            img = img.rotate(180)
        elif orientation == 4:
            img = img.rotate(180).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 5:
            img = img.rotate(-90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 6:
            img = img.rotate(-90, expand=True)
        elif orientation == 7:
            img = img.rotate(90, expand=True).transpose(Image.FLIP_LEFT_RIGHT)
        elif orientation == 8:
            img = img.rotate(90, expand=True)
        
        return img
        
    except Exception:
        return img


def validate_image_file(file):
    """
    Validate an image file before processing.
    Returns (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"
    
    # Check file size
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)
    
    if size > MAX_FILE_SIZE_MB * 1024 * 1024:
        return False, f"File too large. Maximum size is {MAX_FILE_SIZE_MB}MB"
    
    if size == 0:
        return False, "File is empty"
    
    # Verify it's a valid image
    try:
        img = Image.open(file)
        img.verify()  # Verify it's a valid image
        file.seek(0)  # Reset file pointer
        
        # Check dimensions (reject very small images)
        img = Image.open(file)
        width, height = img.size
        file.seek(0)
        
        if width < 100 or height < 100:
            return False, "Image too small. Minimum size is 100x100 pixels"
        
        if width > 10000 or height > 10000:
            return False, "Image too large. Maximum dimensions are 10000x10000 pixels"
        
        return True, None
        
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"


def get_image_dimensions(file_path):
    """Get dimensions of an image file."""
    try:
        with Image.open(file_path) as img:
            return img.size
    except Exception:
        return None, None


def create_blur_preview(image_path, output_path, blur_radius=20):
    """
    Create a blurred preview of an image (for premium features).
    """
    try:
        from PIL import ImageFilter
        
        with Image.open(image_path) as img:
            # Create small thumbnail then scale up for pixelated blur effect
            small = img.copy()
            small.thumbnail((50, 50), Image.Resampling.LANCZOS)
            
            # Scale back up
            blurred = small.resize(img.size, Image.Resampling.NEAREST)
            
            # Apply gaussian blur for smoother effect
            blurred = blurred.filter(ImageFilter.GaussianBlur(radius=blur_radius))
            
            # Save
            if blurred.mode != 'RGB':
                blurred = blurred.convert('RGB')
            blurred.save(output_path, 'JPEG', quality=60)
            
            return True
    except Exception:
        return False

