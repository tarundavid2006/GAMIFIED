"""
Django REST Framework serializers for the gamified learning platform.
Handles data serialization for the offline-first API.
"""
from rest_framework import serializers
from learning.models import (
    Subject, Level, Question, Avatar, DeviceProfile,
    Badge, DeviceLeaderboardEntry, SyncEvent
)


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for subject data with theme information."""
    
    level_count = serializers.SerializerMethodField()
    progress_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Subject
        fields = [
            'id', 'name', 'slug', 'description', 'theme',
            'background_color', 'accent_color', 'animated_logo',
            'theme_assets', 'level_count', 'progress_info', 'order'
        ]
    
    def get_level_count(self, obj):
        """Return total number of active levels in this subject."""
        return obj.levels.filter(is_active=True).count()
    
    def get_progress_info(self, obj):
        """Return progress information if device profile is available."""
        request = self.context.get('request')
        device_id = request.GET.get('device_id') if request else None
        
        if device_id:
            try:
                profile = DeviceProfile.objects.get(device_id=device_id)
                levels_completed = profile.progress_data.get('levels_completed', {})
                completed_count = len(levels_completed.get(obj.slug, []))
                total_levels = self.get_level_count(obj)
                
                return {
                    'completed_levels': completed_count,
                    'total_levels': total_levels,
                    'is_unlocked': completed_count > 0 or obj.slug == 'science'  # Science always unlocked
                }
            except DeviceProfile.DoesNotExist:
                pass
        
        return {
            'completed_levels': 0,
            'total_levels': self.get_level_count(obj),
            'is_unlocked': obj.slug == 'science'  # Science always unlocked
        }


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for question data optimized for offline caching."""
    
    class Meta:
        model = Question
        fields = [
            'id', 'order', 'question_type', 'title', 'payload',
            'correct_answer', 'reward_points', 'time_limit_seconds',
            'hint_text', 'explanation', 'audio_question', 
            'audio_correct', 'audio_incorrect'
        ]


class LevelSerializer(serializers.ModelSerializer):
    """Serializer for level data with questions included for offline caching."""
    
    questions = QuestionSerializer(many=True, read_only=True)
    progress_info = serializers.SerializerMethodField()
    
    class Meta:
        model = Level
        fields = [
            'id', 'order', 'title', 'story_text', 'artwork_url',
            'required_score_to_unlock', 'min_score_to_pass',
            'completion_animation', 'audio_introduction',
            'questions', 'progress_info'
        ]
    
    def get_progress_info(self, obj):
        """Return progress information for this level."""
        request = self.context.get('request')
        device_id = request.GET.get('device_id') if request else None
        
        if device_id:
            try:
                profile = DeviceProfile.objects.get(device_id=device_id)
                scores = profile.progress_data.get('scores', {})
                level_score = scores.get(str(obj.id), {})
                
                return {
                    'is_completed': str(obj.id) in scores,
                    'best_score': level_score.get('score', 0),
                    'attempts': level_score.get('attempts', 0),
                    'best_time': level_score.get('best_time', 0),
                    'is_unlocked': self._is_level_unlocked(obj, profile)
                }
            except DeviceProfile.DoesNotExist:
                pass
        
        return {
            'is_completed': False,
            'best_score': 0,
            'attempts': 0,
            'best_time': 0,
            'is_unlocked': obj.order == 1  # First level always unlocked
        }
    
    def _is_level_unlocked(self, level, profile):
        """Check if level is unlocked based on previous progress."""
        if level.order == 1:
            return True  # First level always unlocked
        
        # Check if previous levels have been completed with sufficient score
        previous_levels = Level.objects.filter(
            subject=level.subject,
            order__lt=level.order,
            is_active=True
        )
        
        scores = profile.progress_data.get('scores', {})
        total_points = 0
        
        for prev_level in previous_levels:
            level_score = scores.get(str(prev_level.id), {})
            if level_score.get('score', 0) >= prev_level.min_score_to_pass:
                total_points += level_score.get('score', 0)
        
        return total_points >= level.required_score_to_unlock


class LevelListSerializer(serializers.ModelSerializer):
    """Simplified serializer for level listing without questions."""
    
    progress_info = serializers.SerializerMethodField()
    question_count = serializers.SerializerMethodField()
    total_points = serializers.SerializerMethodField()
    
    class Meta:
        model = Level
        fields = [
            'id', 'order', 'title', 'story_text', 'artwork_url',
            'required_score_to_unlock', 'min_score_to_pass',
            'question_count', 'total_points', 'progress_info'
        ]
    
    def get_question_count(self, obj):
        return obj.total_questions
    
    def get_total_points(self, obj):
        return obj.total_points
    
    def get_progress_info(self, obj):
        """Same as LevelSerializer but simplified."""
        request = self.context.get('request')
        device_id = request.GET.get('device_id') if request else None
        
        if device_id:
            try:
                profile = DeviceProfile.objects.get(device_id=device_id)
                scores = profile.progress_data.get('scores', {})
                level_score = scores.get(str(obj.id), {})
                
                return {
                    'is_completed': str(obj.id) in scores,
                    'best_score': level_score.get('score', 0),
                    'is_unlocked': obj.order == 1 or self._has_prerequisites(obj, profile)
                }
            except DeviceProfile.DoesNotExist:
                pass
        
        return {
            'is_completed': False,
            'best_score': 0,
            'is_unlocked': obj.order == 1
        }
    
    def _has_prerequisites(self, level, profile):
        """Simple prerequisite check for level listing."""
        scores = profile.progress_data.get('scores', {})
        previous_level_id = str(level.id - 1) if level.id > 1 else None
        
        if previous_level_id:
            prev_score = scores.get(previous_level_id, {})
            return prev_score.get('score', 0) > 0
        
        return True


class AvatarSerializer(serializers.ModelSerializer):
    """Serializer for avatar characters."""
    
    class Meta:
        model = Avatar
        fields = [
            'id', 'name', 'description', 'avatar_image',
            'animated_assets', 'personality_traits', 'voice_lines',
            'unlockable_assets', 'is_default'
        ]


class DeviceProfileSerializer(serializers.ModelSerializer):
    """Serializer for device profiles with full progress data."""
    
    avatar = AvatarSerializer(read_only=True)
    avatar_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = DeviceProfile
        fields = [
            'device_id', 'avatar', 'avatar_id', 'progress_data',
            'last_synced', 'sync_version', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_synced']
    
    def create(self, validated_data):
        """Create new device profile."""
        avatar_id = validated_data.pop('avatar_id', None)
        
        if avatar_id:
            try:
                avatar = Avatar.objects.get(id=avatar_id, is_active=True)
                validated_data['avatar'] = avatar
            except Avatar.DoesNotExist:
                pass
        
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """Update device profile with avatar handling."""
        avatar_id = validated_data.pop('avatar_id', None)
        
        if avatar_id is not None:
            try:
                avatar = Avatar.objects.get(id=avatar_id, is_active=True) if avatar_id else None
                instance.avatar = avatar
            except Avatar.DoesNotExist:
                pass
        
        return super().update(instance, validated_data)


class ProgressSyncSerializer(serializers.Serializer):
    """Serializer for syncing progress data."""
    
    progress_entries = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of progress entries to sync"
    )
    version = serializers.IntegerField(help_text="Client version for conflict resolution")
    last_updated = serializers.DateTimeField(help_text="Timestamp of last local update")
    
    def validate_progress_entries(self, value):
        """Validate progress entries format."""
        required_fields = ['level_id', 'score', 'attempts']
        
        for entry in value:
            for field in required_fields:
                if field not in entry:
                    raise serializers.ValidationError(
                        f"Missing required field '{field}' in progress entry"
                    )
        
        return value


class BadgeSerializer(serializers.ModelSerializer):
    """Serializer for achievement badges."""
    
    class Meta:
        model = Badge
        fields = [
            'id', 'name', 'description', 'badge_type', 'criteria',
            'points_reward', 'rarity_level', 'icon_image', 'icon_animation'
        ]


class LeaderboardEntrySerializer(serializers.ModelSerializer):
    """Serializer for leaderboard entries."""
    
    avatar_name = serializers.SerializerMethodField()
    avatar_image = serializers.SerializerMethodField()
    
    class Meta:
        model = DeviceLeaderboardEntry
        fields = [
            'total_points', 'levels_completed', 'current_streak',
            'badges_earned', 'weekly_points', 'monthly_points',
            'avatar_name', 'avatar_image', 'last_activity'
        ]
    
    def get_avatar_name(self, obj):
        return obj.device_profile.avatar.name if obj.device_profile.avatar else "Anonymous"
    
    def get_avatar_image(self, obj):
        if obj.device_profile.avatar and obj.device_profile.avatar.avatar_image:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.device_profile.avatar.avatar_image.url)
        return None


class SyncEventSerializer(serializers.ModelSerializer):
    """Serializer for sync events."""
    
    class Meta:
        model = SyncEvent
        fields = [
            'id', 'device_profile', 'event_type', 'event_data',
            'created_at', 'is_processed'
        ]
        read_only_fields = ['id', 'created_at', 'is_processed']


class SyncEventCreateSerializer(serializers.Serializer):
    """Serializer for creating sync events."""
    
    events = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of sync events to create"
    )
    
    def validate_events(self, value):
        """Validate event format."""
        valid_event_types = [choice[0] for choice in SyncEvent.EVENT_TYPES]
        
        for event in value:
            if 'event_type' not in event:
                raise serializers.ValidationError("Missing 'event_type' in event")
            if event['event_type'] not in valid_event_types:
                raise serializers.ValidationError(f"Invalid event_type: {event['event_type']}")
            if 'event_data' not in event:
                raise serializers.ValidationError("Missing 'event_data' in event")
        
        return value