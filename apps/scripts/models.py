from django.db import models
from django.contrib.auth.models import User
from knowledge.models import KnowledgeBase


class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    category = models.CharField(max_length=100, default='General')
    knowledge_base = models.ForeignKey(
        KnowledgeBase, on_delete=models.SET_NULL, null=True, blank=True, related_name='projects'
    )
    is_favorite = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.name

    @property
    def script_count(self):
        return self.scripts.count()

    @property
    def knowledge_base_name(self):
        if self.knowledge_base:
            return f"Knowledge: {self.knowledge_base.name}"
        return "No knowledge base"


class Script(models.Model):
    PLATFORM_CHOICES = [
        ('youtube', 'YouTube'),
        ('youtube_shorts', 'YouTube Shorts'),
        ('instagram_reels', 'Instagram Reel'),
        ('tiktok', 'TikTok'),
        ('podcast', 'Podcast'),
        ('movie', 'Movie Screenplay'),
        ('short_film', 'Short film'),
        ('web_series', 'Web Series'),
        ('advertisement', 'Advertisement'),
        ('educational', 'Educational Video'),
        ('custom', 'Custom Script'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
    ]

    SYNC_CHOICES = [
        ('synced', 'Synced'),
        ('waiting_to_sync', 'Edited offline · Waiting to sync'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scripts')
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='scripts')
    knowledge_base = models.ForeignKey(KnowledgeBase, on_delete=models.SET_NULL, null=True, blank=True, related_name='scripts')

    title = models.CharField(max_length=255)
    topic = models.TextField(blank=True, default='')
    description = models.TextField(blank=True, default='')
    audience = models.CharField(max_length=150, default='Students')
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES, default='youtube')
    duration = models.CharField(max_length=50, default='8 min')
    tone = models.CharField(max_length=50, default='Informative')
    language = models.CharField(max_length=50, default='English')
    more_options_notes = models.TextField(blank=True, default='')

    # AI Options
    claude_model = models.CharField(max_length=50, default='claude-3-5-sonnet')
    creativity = models.CharField(max_length=50, default='Balanced')
    script_length = models.CharField(max_length=50, default='Medium')
    use_knowledge_base = models.BooleanField(default=False)

    # Generated outline and content
    outline_data = models.JSONField(default=list, blank=True)
    hook = models.TextField(blank=True, default='')
    introduction = models.TextField(blank=True, default='')
    main_content = models.TextField(blank=True, default='')
    conclusion = models.TextField(blank=True, default='')
    call_to_action = models.TextField(blank=True, default='')
    full_content = models.TextField(blank=True, default='')

    # Stats and status
    version = models.IntegerField(default=1)
    word_count = models.IntegerField(default=0)
    char_count = models.IntegerField(default=0)
    estimated_speaking_minutes = models.FloatField(default=1.0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    sync_status = models.CharField(max_length=50, choices=SYNC_CHOICES, default='synced')
    is_favorite = models.BooleanField(default=False)
    sources_used_count = models.IntegerField(default=3)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    def compute_stats(self):
        text = self.get_full_text()
        words = len(text.split())
        chars = len(text)
        self.word_count = words
        self.char_count = chars
        # Average speaking speed is ~130-150 words per minute
        self.estimated_speaking_minutes = round(words / 140.0, 1) if words > 0 else 0.5

    def get_full_text(self):
        if self.full_content and self.full_content.strip():
            return self.full_content
        parts = []
        if self.hook:
            parts.append(f"HOOK\n{self.hook}")
        if self.introduction:
            parts.append(f"INTRODUCTION\n{self.introduction}")
        if self.main_content:
            parts.append(f"MAIN CONTENT\n{self.main_content}")
        if self.conclusion:
            parts.append(f"CONCLUSION\n{self.conclusion}")
        if self.call_to_action:
            parts.append(f"CALL TO ACTION\n{self.call_to_action}")
        return "\n\n".join(parts)

    def save(self, *args, **kwargs):
        self.compute_stats()
        super().save(*args, **kwargs)


class ScriptVersion(models.Model):
    script = models.ForeignKey(Script, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField()
    content_snapshot = models.TextField()
    note = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']

    def __str__(self):
        return f"{self.script.title} - v{self.version_number}"
