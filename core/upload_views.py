from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import cloudinary.uploader
import json


@login_required
@csrf_exempt
def upload_image(request):
    """Simple image upload to Cloudinary"""
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                request.FILES['image'],
                folder="uploads",
                quality="auto:good",
                fetch_format="auto"
            )
            
            return JsonResponse({
                'success': True,
                'url': result['secure_url'],
                'public_id': result['public_id']
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'No image provided'})


@login_required
def upload_test_page(request):
    """Test page for image upload"""
    return render(request, 'upload_test.html')