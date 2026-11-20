from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System'),
    ]

    MODEL_CHOICES = [
        ('claude-3-5-sonnet', 'Claude Sonnet'),
        ('claude-3-opus', 'Claude Opus'),
        ('claude-3-haiku', 'Claude Haiku'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=150, blank=True, default='')
    plan = models.CharField(max_length=50, default='Pro plan')
    plan_resets_on = models.CharField(max_length=50, default='the 1st')
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='dark')
    language = models.CharField(max_length=50, default='English')
    preferred_model = models.CharField(max_length=50, choices=MODEL_CHOICES, default='claude-3-5-sonnet')
    scripts_generated_count = models.IntegerField(default=24)
    words_generated_count = models.IntegerField(default=38000)
    usage_percentage = models.IntegerField(default=45)

    def __str__(self):
        return f"{self.user.username} Profile"

    def get_initials(self):
        if self.full_name.strip():
            parts = self.full_name.strip().split()
            if len(parts) >= 2:
                return f"{parts[0][0]}{parts[1][0]}".upper()
            return parts[0][:2].upper()
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name[0]}{self.user.last_name[0]}".upper()
        return self.user.username[:2].upper()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            full_name=instance.get_full_name() or instance.username
        )
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
