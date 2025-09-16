"""
Tests for the gamified learning platform models and API.
"""
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import json

from .models import Subject, Level, Question, Avatar, DeviceProfile, Badge


class LearningModelsTestCase(TestCase):
    """Test cases for learning models."""
    
    def setUp(self):
        """Set up test data."""
        self.subject = Subject.objects.create(
            name="Test Science",
            slug="test-science",
            theme="science",
            description="Test science subject",
            background_color="#10B981",
            accent_color="#34D399",
            order=1
        )
        
        self.level = Level.objects.create(
            subject=self.subject,
            order=1,
            title="Test Level 1",
            story_text="Welcome to test level!",
            required_score_to_unlock=0,
            min_score_to_pass=70
        )
        
        self.question = Question.objects.create(
            level=self.level,
            order=1,
            question_type="multiple_choice",
            title="What is 2 + 2?",
            payload={
                "choices": ["3", "4", "5", "6"]
            },
            correct_answer=[1],
            reward_points=10
        )
        
        self.avatar = Avatar.objects.create(
            name="Test Avatar",
            description="A test avatar",
            personality_traits=["curious", "helpful"],
            is_default=True
        )
        
        self.device_profile = DeviceProfile.objects.create(
            device_id="test_device_12345",
            avatar=self.avatar,
            progress_data={
                "total_points": 100,
                "scores": {
                    str(self.level.id): {
                        "score": 85,
                        "attempts": 2,
                        "best_time": 120
                    }
                },
                "badges_earned": []
            }
        )
    
    def test_subject_str_representation(self):
        """Test subject string representation."""
        self.assertEqual(str(self.subject), "Test Science")
    
    def test_subject_slug_auto_generation(self):
        """Test subject slug is auto-generated from name."""
        subject = Subject.objects.create(
            name="New Subject Test",
            theme="math"
        )
        self.assertEqual(subject.slug, "new-subject-test")
    
    def test_level_str_representation(self):
        """Test level string representation."""
        expected = f"{self.subject.name} - Level {self.level.order}: {self.level.title}"
        self.assertEqual(str(self.level), expected)
    
    def test_level_total_points_property(self):
        """Test level total points calculation."""
        # Create another question
        Question.objects.create(
            level=self.level,
            order=2,
            question_type="true_false",
            title="Test question 2",
            payload={"statement": "This is true"},
            correct_answer=True,
            reward_points=15
        )
        
        self.assertEqual(self.level.total_points, 25)  # 10 + 15
    
    def test_device_profile_get_total_points(self):
        """Test device profile total points calculation."""
        self.assertEqual(self.device_profile.get_total_points(), 100)
    
    def test_device_profile_get_completed_levels_count(self):
        """Test completed levels count calculation."""
        # Add more completed levels to progress data
        progress_data = self.device_profile.progress_data.copy()
        progress_data["levels_completed"] = {
            "test-science": [1, 2],
            "math": [1]
        }
        self.device_profile.progress_data = progress_data
        self.device_profile.save()
        
        self.assertEqual(self.device_profile.get_completed_levels_count(), 3)


class LearningAPITestCase(TestCase):
    """Test cases for learning API endpoints."""
    
    def setUp(self):
        """Set up test data and API client."""
        self.client = APIClient()
        
        # Create test data
        self.subject = Subject.objects.create(
            name="API Test Science",
            slug="api-test-science",
            theme="science",
            description="API test science subject",
            background_color="#10B981",
            accent_color="#34D399",
            order=1
        )
        
        self.level = Level.objects.create(
            subject=self.subject,
            order=1,
            title="API Test Level",
            story_text="API test level story",
            required_score_to_unlock=0,
            min_score_to_pass=70
        )
        
        self.question = Question.objects.create(
            level=self.level,
            order=1,
            question_type="multiple_choice",
            title="API test question",
            payload={"choices": ["A", "B", "C", "D"]},
            correct_answer=[1],
            reward_points=10
        )
        
        self.avatar = Avatar.objects.create(
            name="API Test Avatar",
            description="An API test avatar",
            is_default=True
        )
        
        self.device_profile = DeviceProfile.objects.create(
            device_id="api_test_device",
            avatar=self.avatar,
            progress_data={"total_points": 50}
        )
    
    def test_subjects_list_endpoint(self):
        """Test subjects list API endpoint."""
        url = reverse('subject-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        subject_data = response.data['results'][0]
        self.assertEqual(subject_data['name'], 'API Test Science')
        self.assertEqual(subject_data['slug'], 'api-test-science')
        self.assertEqual(subject_data['theme'], 'science')
    
    def test_subject_levels_endpoint(self):
        """Test subject levels API endpoint."""
        url = reverse('subject-levels', kwargs={'slug': self.subject.slug})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        level_data = response.data[0]
        self.assertEqual(level_data['title'], 'API Test Level')
        self.assertEqual(level_data['order'], 1)
    
    def test_level_detail_endpoint(self):
        """Test level detail API endpoint with questions."""
        url = reverse('level-detail', kwargs={'pk': self.level.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        level_data = response.data
        self.assertEqual(level_data['title'], 'API Test Level')
        self.assertEqual(len(level_data['questions']), 1)
        
        question_data = level_data['questions'][0]
        self.assertEqual(question_data['title'], 'API test question')
        self.assertEqual(question_data['question_type'], 'multiple_choice')
    
    def test_avatars_list_endpoint(self):
        """Test avatars list API endpoint."""
        url = reverse('avatar-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        avatar_data = response.data['results'][0]
        self.assertEqual(avatar_data['name'], 'API Test Avatar')
        self.assertEqual(avatar_data['is_default'], True)
    
    def test_device_profile_create_endpoint(self):
        """Test device profile creation API endpoint."""
        url = reverse('deviceprofile-list')
        data = {
            'device_id': 'new_test_device',
            'avatar_id': self.avatar.id,
            'progress_data': {'total_points': 0}
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['device_id'], 'new_test_device')
        self.assertEqual(response.data['avatar']['id'], self.avatar.id)
    
    def test_device_profile_sync_progress_endpoint(self):
        """Test device profile progress sync API endpoint."""
        url = reverse('deviceprofile-sync-progress', kwargs={'device_id': self.device_profile.device_id})
        data = {
            'progress_entries': [
                {
                    'level_id': self.level.id,
                    'score': 90,
                    'attempts': 1,
                    'completion_time': 100
                }
            ],
            'version': 1,
            'last_updated': '2024-01-01T12:00:00Z'
        }
        
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that progress was updated
        self.device_profile.refresh_from_db()
        scores = self.device_profile.progress_data.get('scores', {})
        level_score = scores.get(str(self.level.id), {})
        self.assertEqual(level_score['score'], 90)
        self.assertEqual(level_score['attempts'], 1)
    
    def test_health_check_endpoint(self):
        """Test health check API endpoint."""
        url = reverse('health_check')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
        self.assertIn('timestamp', response.data)
        self.assertIn('version', response.data)


class BadgeTestCase(TestCase):
    """Test cases for badge functionality."""
    
    def setUp(self):
        """Set up test badge data."""
        self.badge = Badge.objects.create(
            name="Test Badge",
            description="A test achievement badge",
            badge_type="completion",
            criteria={"type": "complete_levels", "count": 1},
            points_reward=50,
            rarity_level=1
        )
    
    def test_badge_str_representation(self):
        """Test badge string representation."""
        self.assertEqual(str(self.badge), "Test Badge")
    
    def test_badge_creation_with_criteria(self):
        """Test badge creation with JSON criteria."""
        criteria = {"type": "streak", "days": 7}
        badge = Badge.objects.create(
            name="Streak Badge",
            description="7-day streak",
            badge_type="streak",
            criteria=criteria,
            points_reward=100,
            rarity_level=2
        )
        
        self.assertEqual(badge.criteria, criteria)
        self.assertEqual(badge.points_reward, 100)
        self.assertEqual(badge.rarity_level, 2)