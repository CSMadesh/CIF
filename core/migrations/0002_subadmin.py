from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SubAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('content', 'Content Manager'), ('support', 'Support Manager'), ('moderator', 'Moderator')], max_length=20)),
                ('can_manage_users', models.BooleanField(default=False)),
                ('can_manage_opportunities', models.BooleanField(default=False)),
                ('can_manage_courses', models.BooleanField(default=False)),
                ('can_manage_applications', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='sub_admin', to=settings.AUTH_USER_MODEL)),
                ('assigned_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_subadmins', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
