# Cloudinary Integration Setup

## Overview
Your Django project now uses Cloudinary for image and video uploads instead of local file storage. This provides:
- Automatic image optimization
- CDN delivery
- Unlimited storage
- Image transformations

## Setup Instructions

### 1. Get Cloudinary Credentials
1. Sign up at [Cloudinary](https://cloudinary.com)
2. Go to your [Dashboard](https://cloudinary.com/console)
3. Copy your credentials:
   - Cloud Name
   - API Key
   - API Secret

### 2. Set Environment Variables
Create a `.env` file in your project root:
```bash
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py migrate
```

## Usage

### Profile Avatar Upload
The existing profile form now automatically uploads to Cloudinary:
```python
# In views.py - profile_view function
if 'avatar' in request.FILES:
    profile.avatar = request.FILES['avatar']  # Automatically uploads to Cloudinary
```

### Course Thumbnail/Video Upload
Course creation forms now use Cloudinary:
```python
# In views.py - subadmin_add_course function
if 'thumbnail' in request.FILES:
    course.thumbnail = request.FILES['thumbnail']  # Uploads to 'course_thumbnails' folder
if 'video' in request.FILES:
    course.video = request.FILES['video']  # Uploads to 'course_videos' folder
```

### Direct Upload API
For custom uploads, use the upload endpoint:
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);

fetch('/upload-image/', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('Image URL:', data.url);
        console.log('Public ID:', data.public_id);
    }
});
```

## Testing
Visit `/upload-test/` to test the upload functionality.

## File Organization
- **Avatars**: `avatars/` folder
- **Course Thumbnails**: `course_thumbnails/` folder  
- **Course Videos**: `course_videos/` folder
- **General Uploads**: `uploads/` folder

## Features
- Automatic image optimization
- WebP format conversion
- Responsive image delivery
- Video streaming
- Secure URLs
- Automatic backup

## Production Deployment
For Vercel deployment, add environment variables in your Vercel dashboard:
1. Go to your project settings
2. Add Environment Variables:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`