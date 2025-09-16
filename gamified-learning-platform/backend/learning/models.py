"""
Models for the gamified learning platform.
Designed for offline-first architecture with device-based profiles.
"""
import json
import uuid
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify


class Subject(models.Model):
    """
    Learning subjects like Math, Science, Language, General Knowledge.
    Each subject has its own adventure theme and visual assets.
    """
    SUBJECT_THEMES = [
        ('science', 'Plant Growth Adventure'),
        ('math', 'Mountain Trail Journey'), 
        ('language', 'Storybook Adventure'),
        ('general_knowledge', 'World Map Explorer'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    theme = models.CharField(max_length=50, choices=SUBJECT_THEMES)
    
    # Visual assets
    logo_image = models.ImageField(upload_to='subjects/logos/', blank=True, null=True)
    animated_logo = models.JSONField(
        default=dict, 
        blank=True,
        help_text="Lottie animation JSON for animated logo"
    )
    background_color = models.CharField(max_length=7, default='#4F46E5')
    accent_color = models.CharField(max_length=7, default='#818CF8')
    
    # Adventure theme assets
    theme_assets = models.JSONField(
        default=dict,
        blank=True,
        help_text="Theme-specific visual elements and animations"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name


class Level(models.Model):
    """
    Individual levels within a subject's adventure path.
    Each level contains questions and has story progression.
    """
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='levels')
    order = models.PositiveIntegerField(help_text="Order within subject (1, 2, 3...)")
    title = models.CharField(max_length=200)
    story_text = models.TextField(
        help_text="Story text that appears when starting this level"
    )
    
    # Progression requirements
    required_score_to_unlock = models.PositiveIntegerField(
        default=0,
        help_text="Points needed from previous levels to unlock this level"
    )
    min_score_to_pass = models.PositiveIntegerField(
        default=70,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Minimum score percentage to pass this level"
    )
    
    # Visual assets for level progression
    artwork_url = models.URLField(blank=True, help_text="Level artwork image URL")
    completion_animation = models.JSONField(
        default=dict,
        blank=True,
        help_text="Lottie animation for level completion"
    )
    
    # Audio guidance
    audio_introduction = models.FileField(
        upload_to='audio/intros/',
        blank=True,
        null=True,
        help_text="Audio file played when starting level"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['subject', 'order']
        unique_together = ['subject', 'order']
        verbose_name = "Level"
        verbose_name_plural = "Levels"
    
    def __str__(self):
        return f"{self.subject.name} - Level {self.order}: {self.title}"
    
    @property
    def total_questions(self):
        """Total number of questions in this level."""
        return self.questions.filter(is_active=True).count()
    
    @property
    def total_points(self):
        """Maximum points achievable in this level."""
        return sum(q.reward_points for q in self.questions.filter(is_active=True))


class Question(models.Model):
    """
    Individual questions within levels.
    Supports multiple question types for engaging interactions.
    """
    QUESTION_TYPES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('drag_drop', 'Drag & Drop'),
        ('audio_choice', 'Audio Choice'),
        ('image_choice', 'Image Choice'),
        ('fill_blank', 'Fill in the Blank'),
    ]
    
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='questions')
    order = models.PositiveIntegerField(help_text="Order within level")
    
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    title = models.CharField(max_length=300, help_text="Question text or prompt")
    
    # Question content and assets
    payload = models.JSONField(
        help_text="""
        Question data structure varies by type:
        - multiple_choice: {"choices": ["A", "B", "C"], "images": ["url1", "url2"]}
        - drag_drop: {"items": ["item1", "item2"], "targets": ["target1", "target2"]}
        - audio_choice: {"audio_url": "url", "choices": ["A", "B", "C"]}
        """
    )
    
    # Correct answer and validation
    correct_answer = models.JSONField(
        help_text="Correct answer(s) - format depends on question type"
    )
    
    # Scoring and rewards
    reward_points = models.PositiveIntegerField(default=10)
    time_limit_seconds = models.PositiveIntegerField(
        default=30,
        help_text="Time limit for answering (0 = no limit)"
    )
    
    # Audio and visual feedback
    audio_question = models.FileField(
        upload_to='audio/questions/',
        blank=True,
        null=True,
        help_text="Audio reading of the question"
    )
    audio_correct = models.FileField(
        upload_to='audio/feedback/',
        blank=True,
        null=True,
        help_text="Audio played for correct answers"
    )
    audio_incorrect = models.FileField(
        upload_to='audio/feedback/',
        blank=True,
        null=True,
        help_text="Audio played for incorrect answers"
    )
    
    # Hints and explanations
    hint_text = models.TextField(blank=True, help_text="Hint text if student struggles")
    explanation = models.TextField(blank=True, help_text="Explanation shown after answering")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['level', 'order']
        unique_together = ['level', 'order']
        verbose_name = "Question"
        verbose_name_plural = "Questions"
    
    def __str__(self):
        return f"{self.level} - Q{self.order}: {self.title[:50]}"


class Avatar(models.Model):
    """
    Avatar characters that children can choose.
    Each device can have multiple avatars for sibling sharing.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    # Visual assets
    avatar_image = models.ImageField(upload_to='avatars/', blank=True, null=True)
    animated_assets = models.JSONField(
        default=dict,
        blank=True,
        help_text="""
        Avatar animation assets:
        {"idle": "lottie_json", "happy": "lottie_json", "thinking": "lottie_json"}
        """
    )
    
    # Avatar personality and audio
    personality_traits = models.JSONField(
        default=list,
        blank=True,
        help_text='List of personality traits like ["curious", "helpful", "energetic"]'
    )
    voice_lines = models.JSONField(
        default=dict,
        blank=True,
        help_text='Audio file URLs for different situations'
    )
    
    # Unlockable content
    unlockable_assets = models.JSONField(
        default=dict,
        blank=True,
        help_text="Assets unlocked as player progresses"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['name']
        verbose_name = "Avatar"
        verbose_name_plural = "Avatars"
    
    def __str__(self):
        return self.name


class DeviceProfile(models.Model):
    """
    Device-based profile for offline-first architecture.
    No user accounts - just device ID + selected avatar.
    """
    device_id = models.CharField(
        max_length=255,
        primary_key=True,
        help_text="Hashed device identifier"
    )
    avatar = models.ForeignKey(
        Avatar, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='device_profiles'
    )
    
    # Progress tracking
    progress_data = models.JSONField(
        default=dict,
        help_text="""
        Progress structure:
        {
            "levels_completed": {"subject_slug": [1, 2, 3]},
            "scores": {"level_id": {"score": 85, "attempts": 2, "best_time": 120}},
            "total_points": 1250,
            "badges_earned": ["first_level", "math_master"],
            "current_streak": 5
        }
        """
    )
    
    # Sync metadata
    last_synced = models.DateTimeField(null=True, blank=True)
    sync_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Device Profile"
        verbose_name_plural = "Device Profiles"
    
    def __str__(self):
        avatar_name = self.avatar.name if self.avatar else "No Avatar"
        return f"Device {self.device_id[:8]}... - {avatar_name}"
    
    def get_total_points(self):
        """Calculate total points from progress data."""
        return self.progress_data.get('total_points', 0)
    
    def get_completed_levels_count(self):
        """Count total completed levels across all subjects."""
        levels_completed = self.progress_data.get('levels_completed', {})
        return sum(len(levels) for levels in levels_completed.values())


class Badge(models.Model):
    """
    Achievement badges that players can earn.
    Displayed in the rewards section.
    """
    BADGE_TYPES = [
        ('completion', 'Completion Badge'),
        ('streak', 'Streak Badge'),
        ('performance', 'Performance Badge'),
        ('special', 'Special Achievement'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES)
    
    # Visual assets
    icon_image = models.ImageField(upload_to='badges/', blank=True, null=True)
    icon_animation = models.JSONField(
        default=dict,
        blank=True,
        help_text="Lottie animation for badge unlock"
    )
    
    # Earning criteria
    criteria = models.JSONField(
        help_text="""
        Badge earning criteria:
        {"type": "complete_levels", "subject": "math", "count": 5}
        {"type": "streak", "days": 7}
        {"type": "score", "min_score": 90, "level_count": 10}
        """
    )
    
    # Rewards and rarity
    points_reward = models.PositiveIntegerField(default=50)
    rarity_level = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="1=Common, 5=Legendary"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['rarity_level', 'name']
        verbose_name = "Badge"
        verbose_name_plural = "Badges"
    
    def __str__(self):
        return self.name


class DeviceLeaderboardEntry(models.Model):
    """
    Leaderboard entries for device-based competition.
    Aggregated per device and synced with server.
    """
    device_profile = models.OneToOneField(
        DeviceProfile,
        on_delete=models.CASCADE,
        related_name='leaderboard_entry'
    )
    
    total_points = models.PositiveIntegerField(default=0)
    levels_completed = models.PositiveIntegerField(default=0)
    current_streak = models.PositiveIntegerField(default=0)
    badges_earned = models.PositiveIntegerField(default=0)
    
    # Time-based rankings
    weekly_points = models.PositiveIntegerField(default=0)
    monthly_points = models.PositiveIntegerField(default=0)
    
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-total_points', '-last_activity']
        verbose_name = "Leaderboard Entry"
        verbose_name_plural = "Leaderboard Entries"
    
    def __str__(self):
        avatar_name = self.device_profile.avatar.name if self.device_profile.avatar else "Unknown"
        return f"{avatar_name} - {self.total_points} points"


class SyncEvent(models.Model):
    """
    Queue for offline sync events.
    Stores actions taken offline to be synced when online.
    """
    EVENT_TYPES = [
        ('level_completed', 'Level Completed'),
        ('badge_earned', 'Badge Earned'),
        ('progress_updated', 'Progress Updated'),
        ('avatar_changed', 'Avatar Changed'),
    ]
    
    device_profile = models.ForeignKey(
        DeviceProfile,
        on_delete=models.CASCADE,
        related_name='sync_events'
    )
    
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    event_data = models.JSONField(
        help_text="Event-specific data payload"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    
    # Error handling
    sync_attempts = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    
    class Meta:
        ordering = ['created_at']
        verbose_name = "Sync Event"
        verbose_name_plural = "Sync Events"
    
    def __str__(self):
        return f"{self.event_type} - {self.device_profile.device_id[:8]}... ({self.created_at})"