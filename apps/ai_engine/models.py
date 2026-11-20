from django.db import models
from django.contrib.auth.models import User
from scripts.models import Script


class AIChatMessage(models.Model):
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
    ]

    script = models.ForeignKey(Script, on_delete=models.CASCADE, related_name='chat_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_chat_messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    suggested_action = models.CharField(max_length=50, blank=True, default='')  # 'replace_hook', 'insert_below', etc.
    suggested_snippet = models.TextField(blank=True, default='')
    target_section = models.CharField(max_length=50, blank=True, default='hook')  # 'hook', 'intro', 'main', 'outro'
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.role.capitalize()} on {self.script.title}"


class GenerationLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='generation_logs')
    tool_name = models.CharField(max_length=100)  # 'wizard', 'hook_gen', 'rewriter', 'scene_breakdown', etc.
    input_payload = models.JSONField(default=dict, blank=True)
    output_text = models.TextField(blank=True, default='')
    model_used = models.CharField(max_length=100, default='claude-3-5-sonnet')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.tool_name} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
