from django.db import models
from django.contrib.auth.models import User


class KnowledgeBase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='knowledge_bases')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.user.username})"

    @property
    def document_count(self):
        return self.documents.count()


class KnowledgeDocument(models.Model):
    STATUS_CHOICES = [
        ('indexed', 'Indexed'),
        ('indexing', 'Indexing...'),
        ('failed', 'Failed'),
    ]

    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.CASCADE, related_name='documents')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/docs/', blank=True, null=True)
    file_type = models.CharField(max_length=50, default='PDF')
    file_size_display = models.CharField(max_length=50, default='1.2 MB')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='indexed')
    content_text = models.TextField(blank=True, default='')
    source_url = models.URLField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title
