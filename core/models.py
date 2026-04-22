from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=500, blank=True)
    ai_score = models.IntegerField(default=0)
    profile_views = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Course(models.Model):
    CATEGORY_CHOICES = [
        ('tech', 'Technology'),
        ('business', 'Business'),
        ('freelancing', 'Freelancing'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    duration = models.CharField(max_length=50)
    thumbnail = models.ImageField(upload_to='courses/', blank=True, null=True)
    video = models.FileField(upload_to='course_videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Opportunity(models.Model):
    TYPE_CHOICES = [
        ('internship', 'Internship'),
        ('freelance', 'Freelance'),
        ('gig', 'Gig'),
    ]
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=100)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    category = models.CharField(max_length=100)
    stipend = models.CharField(max_length=50, blank=True)
    deadline = models.DateField(null=True, blank=True)
    is_trending = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company}"


class Application(models.Model):
    STATUS_CHOICES = [
        ('applied', 'Applied'),
        ('reviewing', 'Under Review'),
        ('interview', 'Interview Scheduled'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'opportunity')

    def __str__(self):
        return f"{self.user.username} → {self.opportunity.title}"


class SavedOpportunity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'opportunity')


class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    message = models.TextField()
    reply = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.user.username}: {self.message[:40]}"


class SubAdmin(models.Model):
    ROLE_CHOICES = [
        ('content', 'Content Manager'),
        ('support', 'Support Manager'),
        ('moderator', 'Moderator'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sub_admin')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    can_manage_users = models.BooleanField(default=False)
    can_manage_opportunities = models.BooleanField(default=False)
    can_manage_courses = models.BooleanField(default=False)
    can_manage_applications = models.BooleanField(default=False)
    assigned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_subadmins')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"
