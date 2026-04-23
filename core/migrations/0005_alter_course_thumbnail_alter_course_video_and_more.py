import os
from django.db import migrations, models


def _use_cloudinary():
    key = os.environ.get('CLOUDINARY_API_KEY', '')
    return bool(key and key != 'your_api_key')


def _thumbnail_field():
    if _use_cloudinary():
        import cloudinary.models
        return cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='thumbnail')
    return models.ImageField(blank=True, null=True, upload_to='course_thumbnails/')


def _video_field():
    if _use_cloudinary():
        import cloudinary.models
        return cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='video')
    return models.FileField(blank=True, null=True, upload_to='course_videos/')


def _avatar_field():
    if _use_cloudinary():
        import cloudinary.models
        return cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='avatar')
    return models.ImageField(blank=True, null=True, upload_to='avatars/')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_course_video'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='thumbnail',
            field=_thumbnail_field(),
        ),
        migrations.AlterField(
            model_name='course',
            name='video',
            field=_video_field(),
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=_avatar_field(),
        ),
    ]
