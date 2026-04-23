#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ixova.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print(f"Email Backend: {settings.EMAIL_BACKEND}")
print(f"Email Host: {settings.EMAIL_HOST}")
print(f"Email Port: {settings.EMAIL_PORT}")
print(f"Email User: {settings.EMAIL_HOST_USER}")
print(f"Email Password: {'***' if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
print()

try:
    print("Attempting to send test email...")
    result = send_mail(
        subject='IXOVA Test Email',
        message='This is a test OTP email.\n\nYour OTP is: 123456',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['madeshcs28@gmail.com'],
        fail_silently=False,
    )
    print(f"✓ Email sent successfully! (result: {result})")
except Exception as e:
    print(f"✗ Email error: {type(e).__name__}")
    print(f"✗ Details: {e}")
    import traceback
    traceback.print_exc()
