"""
URL configuration for the API endpoints.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    SubjectViewSet, LevelViewSet, AvatarViewSet, DeviceProfileViewSet,
    BadgeViewSet, LeaderboardView, sync_events, health_check
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'subjects', SubjectViewSet)
router.register(r'levels', LevelViewSet)
router.register(r'avatars', AvatarViewSet)
router.register(r'device/profiles', DeviceProfileViewSet)
router.register(r'badges', BadgeViewSet)

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Additional endpoints
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('sync/events/', sync_events, name='sync_events'),
    path('health/', health_check, name='health_check'),
]