import cloudinary.uploader
from django.core.files.storage import default_storage


def upload_to_cloudinary(file, folder="uploads", public_id=None):
    """
    Upload file to Cloudinary
    
    Args:
        file: Django file object
        folder: Cloudinary folder name
        public_id: Custom public ID (optional)
    
    Returns:
        dict: Upload result with 'secure_url' and 'public_id'
    """
    try:
        upload_options = {
            'folder': folder,
            'resource_type': 'auto',
            'quality': 'auto:good',
            'fetch_format': 'auto'
        }
        
        if public_id:
            upload_options['public_id'] = public_id
            
        result = cloudinary.uploader.upload(file, **upload_options)
        return {
            'success': True,
            'secure_url': result['secure_url'],
            'public_id': result['public_id']
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


def delete_from_cloudinary(public_id):
    """Delete file from Cloudinary"""
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    except Exception:
        return False