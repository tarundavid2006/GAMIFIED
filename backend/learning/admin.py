"""
Django admin configuration for the learning platform.
Provides a user-friendly interface for content management.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
import json

from .models import (
    Subject, Level, Question, Avatar, DeviceProfile, 
    Badge, DeviceLeaderboardEntry, SyncEvent
)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Admin interface for managing learning subjects."""
    
    list_display = ['name', 'theme', 'order', 'is_active', 'level_count', 'created_at']
    list_filter = ['theme', 'is_active', 'created_at']
    list_editable = ['order', 'is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'theme', 'order', 'is_active')
        }),
        ('Visual Theme', {
            'fields': ('background_color', 'accent_color', 'logo_image', 'animated_logo'),
            'classes': ('collapse',)
        }),
        ('Theme Assets', {
            'fields': ('theme_assets',),
            'classes': ('collapse',)
        }),
    )
    
    def level_count(self, obj):
        """Display number of levels in this subject."""
        count = obj.levels.count()
        url = reverse('admin:learning_level_changelist') + f'?subject__id__exact={obj.id}'
        return format_html('<a href="{}">{} levels</a>', url, count)
    level_count.short_description = 'Levels'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('levels')


class QuestionInline(admin.TabularInline):
    """Inline admin for questions within levels."""
    
    model = Question
    extra = 0
    fields = ['order', 'question_type', 'title', 'reward_points', 'is_active']
    readonly_fields = ['created_at']
    ordering = ['order']


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    """Admin interface for managing levels within subjects."""
    
    list_display = [
        'subject', 'order', 'title', 'question_count', 
        'total_points', 'min_score_to_pass', 'is_active'
    ]
    list_filter = ['subject', 'is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['title', 'story_text', 'subject__name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('subject', 'order', 'title', 'story_text', 'is_active')
        }),
        ('Progression Settings', {
            'fields': ('required_score_to_unlock', 'min_score_to_pass')
        }),
        ('Media Assets', {
            'fields': ('artwork_url', 'audio_introduction', 'completion_animation'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [QuestionInline]
    
    def question_count(self, obj):
        """Display number of questions in this level."""
        return obj.total_questions
    question_count.short_description = 'Questions'
    
    def total_points(self, obj):
        """Display total points available in this level."""
        return obj.total_points
    total_points.short_description = 'Max Points'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin interface for managing individual questions."""
    
    list_display = [
        'level', 'order', 'question_type', 'title_truncated', 
        'reward_points', 'time_limit_seconds', 'is_active'
    ]
    list_filter = ['question_type', 'is_active', 'level__subject', 'created_at']
    list_editable = ['is_active']
    search_fields = ['title', 'level__title', 'level__subject__name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('level', 'order', 'question_type', 'title', 'is_active')
        }),
        ('Question Content', {
            'fields': ('payload', 'correct_answer', 'hint_text', 'explanation')
        }),
        ('Scoring & Timing', {
            'fields': ('reward_points', 'time_limit_seconds')
        }),
        ('Audio Files', {
            'fields': ('audio_question', 'audio_correct', 'audio_incorrect'),
            'classes': ('collapse',)
        }),
    )
    
    def title_truncated(self, obj):
        """Display truncated question title."""
        return obj.title[:50] + "..." if len(obj.title) > 50 else obj.title
    title_truncated.short_description = 'Question'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('level', 'level__subject')


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    """Admin interface for managing avatar characters."""
    
    list_display = ['name', 'is_active', 'is_default', 'device_count', 'created_at']
    list_filter = ['is_active', 'is_default', 'created_at']
    list_editable = ['is_active', 'is_default']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'is_active', 'is_default')
        }),
        ('Visual Assets', {
            'fields': ('avatar_image', 'animated_assets', 'unlockable_assets'),
            'classes': ('collapse',)
        }),
        ('Personality', {
            'fields': ('personality_traits', 'voice_lines'),
            'classes': ('collapse',)
        }),
    )
    
    def device_count(self, obj):
        """Display number of devices using this avatar."""
        count = obj.device_profiles.count()
        if count > 0:
            url = reverse('admin:learning_deviceprofile_changelist') + f'?avatar__id__exact={obj.id}'
            return format_html('<a href="{}">{} devices</a>', url, count)
        return "0 devices"
    device_count.short_description = 'Used by'


@admin.register(DeviceProfile)
class DeviceProfileAdmin(admin.ModelAdmin):
    """Admin interface for managing device profiles."""
    
    list_display = [
        'device_id_short', 'avatar', 'total_points', 'levels_completed', 
        'last_synced', 'created_at'
    ]
    list_filter = ['avatar', 'last_synced', 'created_at']
    search_fields = ['device_id', 'avatar__name']
    readonly_fields = ['device_id', 'sync_version', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Device Information', {
            'fields': ('device_id', 'avatar', 'sync_version')
        }),
        ('Progress Data', {
            'fields': ('progress_data_formatted',),
            'classes': ('collapse',)
        }),
        ('Sync Information', {
            'fields': ('last_synced', 'created_at', 'updated_at')
        }),
    )
    
    def device_id_short(self, obj):
        """Display shortened device ID."""
        return f"{obj.device_id[:12]}..."
    device_id_short.short_description = 'Device ID'
    
    def total_points(self, obj):
        """Display total points from progress data."""
        return obj.get_total_points()
    total_points.short_description = 'Points'
    
    def levels_completed(self, obj):
        """Display completed levels count."""
        return obj.get_completed_levels_count()
    levels_completed.short_description = 'Completed'
    
    def progress_data_formatted(self, obj):
        """Display formatted progress data."""
        return format_html(
            '<pre>{}</pre>', 
            json.dumps(obj.progress_data, indent=2)
        )
    progress_data_formatted.short_description = 'Progress Data'
    progress_data_formatted.allow_tags = True


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    """Admin interface for managing achievement badges."""
    
    list_display = [
        'name', 'badge_type', 'rarity_level', 'points_reward', 
        'is_active', 'created_at'
    ]
    list_filter = ['badge_type', 'rarity_level', 'is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['name', 'description']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'badge_type', 'is_active')
        }),
        ('Earning Criteria', {
            'fields': ('criteria', 'points_reward', 'rarity_level')
        }),
        ('Visual Assets', {
            'fields': ('icon_image', 'icon_animation'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DeviceLeaderboardEntry)
class DeviceLeaderboardEntryAdmin(admin.ModelAdmin):
    """Admin interface for viewing leaderboard entries."""
    
    list_display = [
        'device_profile', 'avatar_name', 'total_points', 'levels_completed',
        'current_streak', 'badges_earned', 'last_activity'
    ]
    list_filter = ['last_activity', 'created_at']
    search_fields = ['device_profile__device_id', 'device_profile__avatar__name']
    readonly_fields = ['device_profile', 'created_at', 'last_activity']
    
    def avatar_name(self, obj):
        """Display avatar name."""
        return obj.device_profile.avatar.name if obj.device_profile.avatar else "No Avatar"
    avatar_name.short_description = 'Avatar'
    
    def has_add_permission(self, request):
        return False  # Entries are created automatically


@admin.register(SyncEvent)
class SyncEventAdmin(admin.ModelAdmin):
    """Admin interface for viewing sync events."""
    
    list_display = [
        'device_profile', 'event_type', 'created_at', 
        'is_processed', 'sync_attempts', 'processed_at'
    ]
    list_filter = ['event_type', 'is_processed', 'created_at']
    search_fields = ['device_profile__device_id', 'event_type']
    readonly_fields = [
        'device_profile', 'event_type', 'event_data_formatted',
        'created_at', 'processed_at'
    ]
    
    fieldsets = (
        ('Event Information', {
            'fields': ('device_profile', 'event_type', 'event_data_formatted')
        }),
        ('Processing Status', {
            'fields': ('is_processed', 'sync_attempts', 'last_error', 'processed_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    def event_data_formatted(self, obj):
        """Display formatted event data."""
        return format_html(
            '<pre>{}</pre>', 
            json.dumps(obj.event_data, indent=2)
        )
    event_data_formatted.short_description = 'Event Data'
    event_data_formatted.allow_tags = True
    
    def has_add_permission(self, request):
        return False  # Events are created automatically


# Customize admin site headers
admin.site.site_header = "Gamified Learning Platform Admin"
admin.site.site_title = "Learning Platform"
admin.site.index_title = "Content Management"