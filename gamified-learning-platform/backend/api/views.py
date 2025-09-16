"""
API views for the gamified learning platform.
Implements offline-first sync endpoints for device-based profiles.
"""
import logging
from datetime import datetime, timezone
from django.utils import timezone as django_timezone
from rest_framework import viewsets, status, generics
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

from learning.models import (
    Subject, Level, Question, Avatar, DeviceProfile,
    Badge, DeviceLeaderboardEntry, SyncEvent
)
from .serializers import (
    SubjectSerializer, LevelSerializer, LevelListSerializer, QuestionSerializer,
    AvatarSerializer, DeviceProfileSerializer, ProgressSyncSerializer,
    BadgeSerializer, LeaderboardEntrySerializer, SyncEventCreateSerializer
)

logger = logging.getLogger(__name__)


class SubjectViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for learning subjects with adventure themes.
    Supports device-specific progress information.
    """
    queryset = Subject.objects.filter(is_active=True).order_by('order')
    serializer_class = SubjectSerializer
    lookup_field = 'slug'
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='device_id',
                description='Device ID for progress information',
                required=False,
                type=str
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """List all subjects with optional progress info."""
        return super().list(request, *args, **kwargs)
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='device_id',
                description='Device ID for progress information',
                required=False,
                type=str
            )
        ]
    )
    @action(detail=True, methods=['get'])
    def levels(self, request, slug=None):
        """Get levels for a specific subject."""
        subject = self.get_object()
        levels = Level.objects.filter(
            subject=subject,
            is_active=True
        ).order_by('order').prefetch_related('questions')
        
        serializer = LevelListSerializer(levels, many=True, context={'request': request})
        return Response(serializer.data)


class LevelViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for levels with questions for offline caching.
    """
    queryset = Level.objects.filter(is_active=True).select_related('subject')
    serializer_class = LevelSerializer
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='device_id',
                description='Device ID for progress information',
                required=False,
                type=str
            )
        ]
    )
    def retrieve(self, request, *args, **kwargs):
        """Get level details with all questions for offline caching."""
        return super().retrieve(request, *args, **kwargs)
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """Get questions for a specific level (alternative endpoint)."""
        level = self.get_object()
        questions = level.questions.filter(is_active=True).order_by('order')
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)


class AvatarViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for avatar characters.
    """
    queryset = Avatar.objects.filter(is_active=True).order_by('name')
    serializer_class = AvatarSerializer


class DeviceProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for device-based profiles with progress sync.
    """
    queryset = DeviceProfile.objects.all()
    serializer_class = DeviceProfileSerializer
    lookup_field = 'device_id'
    
    @extend_schema(
        request=ProgressSyncSerializer,
        responses={200: DeviceProfileSerializer}
    )
    @action(detail=True, methods=['patch'])
    def sync_progress(self, request, device_id=None):
        """
        Sync progress data with conflict resolution.
        Uses last-write-wins for same score, highest score otherwise.
        """
        try:
            profile = self.get_object()
        except DeviceProfile.DoesNotExist:
            return Response(
                {'error': 'Device profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = ProgressSyncSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        client_entries = validated_data['progress_entries']
        client_version = validated_data['version']
        client_timestamp = validated_data['last_updated']
        
        # Conflict resolution logic
        server_progress = profile.progress_data.copy()
        server_scores = server_progress.get('scores', {})
        updated_scores = server_scores.copy()
        
        conflicts_resolved = []
        
        for entry in client_entries:
            level_id = str(entry['level_id'])
            client_score = entry['score']
            client_attempts = entry['attempts']
            client_time = entry.get('completion_time', 0)
            
            server_entry = server_scores.get(level_id, {})
            server_score = server_entry.get('score', 0)
            
            # Conflict resolution: keep highest score, or last-write-wins if equal
            if client_score > server_score:
                # Client has better score
                updated_scores[level_id] = {
                    'score': client_score,
                    'attempts': client_attempts,
                    'best_time': client_time,
                    'last_updated': client_timestamp.isoformat()
                }
                conflicts_resolved.append({
                    'level_id': level_id,
                    'resolution': 'client_higher_score'
                })
            elif client_score == server_score and client_timestamp > profile.last_synced:
                # Same score but client is more recent
                updated_scores[level_id] = {
                    'score': client_score,
                    'attempts': client_attempts,
                    'best_time': client_time,
                    'last_updated': client_timestamp.isoformat()
                }
                conflicts_resolved.append({
                    'level_id': level_id,
                    'resolution': 'client_more_recent'
                })
        
        # Update server progress
        server_progress['scores'] = updated_scores
        
        # Recalculate total points
        total_points = sum(entry.get('score', 0) for entry in updated_scores.values())
        server_progress['total_points'] = total_points
        
        # Update progress data
        profile.progress_data = server_progress
        profile.sync_version = client_version + 1
        profile.last_synced = django_timezone.now()
        profile.save()
        
        # Update leaderboard entry
        self._update_leaderboard_entry(profile)
        
        logger.info(f"Synced progress for device {device_id}: {len(conflicts_resolved)} conflicts resolved")
        
        response_data = DeviceProfileSerializer(profile).data
        response_data['sync_result'] = {
            'conflicts_resolved': conflicts_resolved,
            'server_version': profile.sync_version,
            'synced_at': profile.last_synced
        }
        
        return Response(response_data)
    
    def _update_leaderboard_entry(self, profile):
        """Update or create leaderboard entry for the profile."""
        entry, created = DeviceLeaderboardEntry.objects.get_or_create(
            device_profile=profile,
            defaults={
                'total_points': profile.get_total_points(),
                'levels_completed': profile.get_completed_levels_count(),
                'current_streak': profile.progress_data.get('current_streak', 0),
                'badges_earned': len(profile.progress_data.get('badges_earned', []))
            }
        )
        
        if not created:
            entry.total_points = profile.get_total_points()
            entry.levels_completed = profile.get_completed_levels_count()
            entry.current_streak = profile.progress_data.get('current_streak', 0)
            entry.badges_earned = len(profile.progress_data.get('badges_earned', []))
            entry.save()


class BadgeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for achievement badges.
    """
    queryset = Badge.objects.filter(is_active=True).order_by('rarity_level', 'name')
    serializer_class = BadgeSerializer


class LeaderboardView(generics.ListAPIView):
    """
    View for global leaderboard data.
    """
    serializer_class = LeaderboardEntrySerializer
    
    def get_queryset(self):
        """Get leaderboard entries with optional filtering."""
        queryset = DeviceLeaderboardEntry.objects.select_related(
            'device_profile__avatar'
        ).order_by('-total_points', '-last_activity')
        
        # Optional filtering
        time_period = self.request.query_params.get('period', 'all')
        if time_period == 'weekly':
            queryset = queryset.order_by('-weekly_points', '-last_activity')
        elif time_period == 'monthly':
            queryset = queryset.order_by('-monthly_points', '-last_activity')
        
        limit = int(self.request.query_params.get('limit', 50))
        return queryset[:limit]


@api_view(['POST'])
@extend_schema(
    request=SyncEventCreateSerializer,
    responses={201: {'description': 'Events queued successfully'}}
)
def sync_events(request):
    """
    Queue sync events for offline actions.
    These are processed asynchronously when the device comes online.
    """
    serializer = SyncEventCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    device_id = request.data.get('device_id')
    if not device_id:
        return Response(
            {'error': 'device_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        profile = DeviceProfile.objects.get(device_id=device_id)
    except DeviceProfile.DoesNotExist:
        return Response(
            {'error': 'Device profile not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    events_data = serializer.validated_data['events']
    created_events = []
    
    for event_data in events_data:
        event = SyncEvent.objects.create(
            device_profile=profile,
            event_type=event_data['event_type'],
            event_data=event_data['event_data']
        )
        created_events.append({
            'id': event.id,
            'event_type': event.event_type,
            'created_at': event.created_at
        })
        
        # Process some events immediately for real-time feedback
        if event_data['event_type'] in ['level_completed', 'badge_earned']:
            _process_sync_event(event)
    
    logger.info(f"Created {len(created_events)} sync events for device {device_id}")
    
    return Response({
        'events_created': len(created_events),
        'events': created_events
    }, status=status.HTTP_201_CREATED)


def _process_sync_event(event):
    """
    Process a sync event immediately.
    This handles real-time updates for important events.
    """
    try:
        if event.event_type == 'level_completed':
            _process_level_completion(event)
        elif event.event_type == 'badge_earned':
            _process_badge_earned(event)
        
        event.is_processed = True
        event.processed_at = django_timezone.now()
        event.save()
        
    except Exception as e:
        event.last_error = str(e)
        event.sync_attempts += 1
        event.save()
        logger.error(f"Error processing sync event {event.id}: {e}")


def _process_level_completion(event):
    """Process level completion event."""
    profile = event.device_profile
    event_data = event.event_data
    
    level_id = str(event_data.get('level_id'))
    score = event_data.get('score', 0)
    completion_time = event_data.get('completion_time', 0)
    
    # Update progress data
    progress = profile.progress_data.copy()
    scores = progress.get('scores', {})
    
    # Only update if this is a better score
    current_score = scores.get(level_id, {}).get('score', 0)
    if score > current_score:
        scores[level_id] = {
            'score': score,
            'attempts': scores.get(level_id, {}).get('attempts', 0) + 1,
            'best_time': completion_time,
            'completed_at': datetime.now(timezone.utc).isoformat()
        }
        progress['scores'] = scores
        
        # Update total points
        progress['total_points'] = sum(s.get('score', 0) for s in scores.values())
        
        profile.progress_data = progress
        profile.save()


def _process_badge_earned(event):
    """Process badge earned event."""
    profile = event.device_profile
    event_data = event.event_data
    
    badge_id = event_data.get('badge_id')
    
    # Update progress data
    progress = profile.progress_data.copy()
    badges = progress.get('badges_earned', [])
    
    if badge_id not in badges:
        badges.append(badge_id)
        progress['badges_earned'] = badges
        
        # Add badge points
        try:
            badge = Badge.objects.get(id=badge_id)
            progress['total_points'] = progress.get('total_points', 0) + badge.points_reward
        except Badge.DoesNotExist:
            pass
        
        profile.progress_data = progress
        profile.save()


@api_view(['GET'])
def health_check(request):
    """
    Simple health check endpoint.
    """
    return Response({
        'status': 'healthy',
        'timestamp': django_timezone.now(),
        'version': '1.0.0'
    })