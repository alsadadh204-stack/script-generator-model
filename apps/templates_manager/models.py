from django.db import models
from django.contrib.auth.models import User


class ScriptTemplate(models.Model):
    CATEGORY_CHOICES = [
        ('all', 'All'),
        ('video', 'Video'),
        ('film', 'Film'),
        ('audio', 'Audio'),
        ('business', 'Business'),
    ]

    name = models.CharField(max_length=150)
    tagline = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='video')
    default_platform = models.CharField(max_length=50, default='youtube')
    default_duration = models.CharField(max_length=50, default='8 min')
    default_tone = models.CharField(max_length=50, default='Informative')
    icon_type = models.CharField(max_length=50, default='script')
    is_builtin = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='custom_templates')
    structure_outline = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name
