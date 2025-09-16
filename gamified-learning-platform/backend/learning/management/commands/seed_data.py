"""
Django management command to seed sample data for the learning platform.
Creates subjects, levels, questions, avatars, and badges with example content.
"""
import json
from django.core.management.base import BaseCommand
from django.db import transaction
from learning.models import Subject, Level, Question, Avatar, Badge


class Command(BaseCommand):
    help = 'Seeds the database with sample learning content'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing data before seeding',
        )
    
    def handle(self, *args, **options):
        if options['reset']:
            self.stdout.write('Resetting existing data...')
            Subject.objects.all().delete()
            Avatar.objects.all().delete()
            Badge.objects.all().delete()
        
        with transaction.atomic():
            self._create_avatars()
            self._create_subjects_and_levels()
            self._create_badges()
        
        self.stdout.write(
            self.style.SUCCESS('Successfully seeded database with sample data!')
        )
    
    def _create_avatars(self):
        """Create sample avatar characters."""
        self.stdout.write('Creating avatars...')
        
        avatars = [
            {
                'name': 'Mango the Explorer',
                'description': 'A curious orange mango who loves adventures!',
                'personality_traits': ['curious', 'brave', 'helpful'],
                'animated_assets': {
                    'idle': {'type': 'lottie', 'src': '/media/lottie/mango_idle.json'},
                    'happy': {'type': 'lottie', 'src': '/media/lottie/mango_happy.json'},
                    'thinking': {'type': 'lottie', 'src': '/media/lottie/mango_thinking.json'}
                },
                'voice_lines': {
                    'greeting': '/media/audio/mango_hello.mp3',
                    'encouragement': '/media/audio/mango_good_job.mp3',
                    'hint': '/media/audio/mango_hint.mp3'
                },
                'is_default': True
            },
            {
                'name': 'Luna the Wise Owl',
                'description': 'A clever owl who knows lots of interesting facts!',
                'personality_traits': ['wise', 'patient', 'encouraging'],
                'animated_assets': {
                    'idle': {'type': 'lottie', 'src': '/media/lottie/owl_idle.json'},
                    'happy': {'type': 'lottie', 'src': '/media/lottie/owl_happy.json'},
                    'thinking': {'type': 'lottie', 'src': '/media/lottie/owl_thinking.json'}
                },
                'voice_lines': {
                    'greeting': '/media/audio/owl_hello.mp3',
                    'encouragement': '/media/audio/owl_excellent.mp3',
                    'hint': '/media/audio/owl_hint.mp3'
                }
            },
            {
                'name': 'Rocket the Space Dog',
                'description': 'A friendly space dog who loves math and science!',
                'personality_traits': ['energetic', 'playful', 'smart'],
                'animated_assets': {
                    'idle': {'type': 'lottie', 'src': '/media/lottie/dog_idle.json'},
                    'happy': {'type': 'lottie', 'src': '/media/lottie/dog_happy.json'},
                    'thinking': {'type': 'lottie', 'src': '/media/lottie/dog_thinking.json'}
                },
                'voice_lines': {
                    'greeting': '/media/audio/dog_woof.mp3',
                    'encouragement': '/media/audio/dog_good.mp3',
                    'hint': '/media/audio/dog_hint.mp3'
                }
            },
            {
                'name': 'Coral the Sea Friend',
                'description': 'A gentle sea creature who loves languages and stories!',
                'personality_traits': ['gentle', 'creative', 'supportive'],
                'animated_assets': {
                    'idle': {'type': 'lottie', 'src': '/media/lottie/coral_idle.json'},
                    'happy': {'type': 'lottie', 'src': '/media/lottie/coral_happy.json'},
                    'thinking': {'type': 'lottie', 'src': '/media/lottie/coral_thinking.json'}
                },
                'voice_lines': {
                    'greeting': '/media/audio/coral_hello.mp3',
                    'encouragement': '/media/audio/coral_wonderful.mp3',
                    'hint': '/media/audio/coral_hint.mp3'
                }
            }
        ]
        
        for avatar_data in avatars:
            avatar, created = Avatar.objects.get_or_create(
                name=avatar_data['name'],
                defaults=avatar_data
            )
            if created:
                self.stdout.write(f'  Created avatar: {avatar.name}')
    
    def _create_subjects_and_levels(self):
        """Create subjects with levels and questions."""
        self.stdout.write('Creating subjects and levels...')
        
        subjects_data = [
            {
                'name': 'Science',
                'slug': 'science',
                'description': 'Explore the wonders of nature and how things work!',
                'theme': 'science',
                'background_color': '#10B981',
                'accent_color': '#34D399',
                'order': 1,
                'animated_logo': {
                    'type': 'lottie',
                    'src': '/media/lottie/science_logo.json'
                },
                'theme_assets': {
                    'plant_stages': [
                        '/media/images/seed.png',
                        '/media/images/sprout.png',
                        '/media/images/sapling.png',
                        '/media/images/flowering.png',
                        '/media/images/tree.png'
                    ]
                }
            },
            {
                'name': 'Math',
                'slug': 'math',
                'description': 'Climb the mountain of numbers and shapes!',
                'theme': 'math',
                'background_color': '#3B82F6',
                'accent_color': '#60A5FA',
                'order': 2,
                'animated_logo': {
                    'type': 'lottie',
                    'src': '/media/lottie/math_logo.json'
                },
                'theme_assets': {
                    'mountain_path': [
                        '/media/images/base_camp.png',
                        '/media/images/first_checkpoint.png',
                        '/media/images/mid_mountain.png',
                        '/media/images/high_peak.png',
                        '/media/images/summit.png'
                    ]
                }
            },
            {
                'name': 'Language',
                'slug': 'language',
                'description': 'Open the magical book of words and stories!',
                'theme': 'language',
                'background_color': '#8B5CF6',
                'accent_color': '#A78BFA',
                'order': 3,
                'animated_logo': {
                    'type': 'lottie',
                    'src': '/media/lottie/language_logo.json'
                },
                'theme_assets': {
                    'book_pages': [
                        '/media/images/book_cover.png',
                        '/media/images/page_1.png',
                        '/media/images/page_2.png',
                        '/media/images/page_3.png',
                        '/media/images/book_complete.png'
                    ]
                }
            },
            {
                'name': 'General Knowledge',
                'slug': 'general_knowledge',
                'description': 'Discover amazing facts about our world!',
                'theme': 'general_knowledge',
                'background_color': '#F59E0B',
                'accent_color': '#FCD34D',
                'order': 4,
                'animated_logo': {
                    'type': 'lottie',
                    'src': '/media/lottie/gk_logo.json'
                },
                'theme_assets': {
                    'world_map': [
                        '/media/images/continent_1.png',
                        '/media/images/continent_2.png',
                        '/media/images/continent_3.png',
                        '/media/images/continent_4.png',
                        '/media/images/world_complete.png'
                    ]
                }
            }
        ]
        
        for subject_data in subjects_data:
            subject, created = Subject.objects.get_or_create(
                slug=subject_data['slug'],
                defaults=subject_data
            )
            if created:
                self.stdout.write(f'  Created subject: {subject.name}')
            
            # Create levels for this subject
            self._create_levels_for_subject(subject)
    
    def _create_levels_for_subject(self, subject):
        """Create levels and questions for a specific subject."""
        levels_data = self._get_levels_data(subject.slug)
        
        for level_data in levels_data:
            level, created = Level.objects.get_or_create(
                subject=subject,
                order=level_data['order'],
                defaults={
                    'title': level_data['title'],
                    'story_text': level_data['story_text'],
                    'required_score_to_unlock': level_data.get('required_score_to_unlock', 0),
                    'min_score_to_pass': level_data.get('min_score_to_pass', 70),
                    'artwork_url': level_data.get('artwork_url', ''),
                    'completion_animation': level_data.get('completion_animation', {})
                }
            )
            if created:
                self.stdout.write(f'    Created level: {level.title}')
            
            # Create questions for this level
            for question_data in level_data.get('questions', []):
                question, created = Question.objects.get_or_create(
                    level=level,
                    order=question_data['order'],
                    defaults={
                        'question_type': question_data['type'],
                        'title': question_data['title'],
                        'payload': question_data['payload'],
                        'correct_answer': question_data['correct_answer'],
                        'reward_points': question_data.get('reward_points', 10),
                        'time_limit_seconds': question_data.get('time_limit', 30),
                        'hint_text': question_data.get('hint', ''),
                        'explanation': question_data.get('explanation', '')
                    }
                )
                if created:
                    self.stdout.write(f'      Created question: {question.title[:30]}...')
    
    def _get_levels_data(self, subject_slug):
        """Return level data for each subject."""
        if subject_slug == 'science':
            return [
                {
                    'order': 1,
                    'title': 'Plant a Seed',
                    'story_text': 'Welcome to our garden! Let\'s start by planting a tiny seed and watch it grow into something amazing!',
                    'artwork_url': '/media/images/seed_level.png',
                    'questions': [
                        {
                            'order': 1,
                            'type': 'multiple_choice',
                            'title': 'What do plants need to grow?',
                            'payload': {
                                'choices': ['Water and sunlight', 'Only water', 'Only air', 'Nothing'],
                                'images': ['/media/images/plant_needs.png']
                            },
                            'correct_answer': [0],
                            'reward_points': 10,
                            'explanation': 'Plants need water, sunlight, and air to grow healthy and strong!'
                        },
                        {
                            'order': 2,
                            'type': 'image_choice',
                            'title': 'Which of these is a seed?',
                            'payload': {
                                'images': [
                                    '/media/images/seed.png',
                                    '/media/images/rock.png',
                                    '/media/images/leaf.png',
                                    '/media/images/flower.png'
                                ]
                            },
                            'correct_answer': [0],
                            'reward_points': 10,
                            'hint': 'Seeds are small and contain everything needed to grow a new plant!'
                        }
                    ]
                },
                {
                    'order': 2,
                    'title': 'First Sprout',
                    'story_text': 'Look! Your seed has started to grow! A tiny green sprout is pushing through the soil.',
                    'required_score_to_unlock': 15,
                    'questions': [
                        {
                            'order': 1,
                            'type': 'true_false',
                            'title': 'Plants grow toward the light.',
                            'payload': {'statement': 'Plants grow toward the light'},
                            'correct_answer': True,
                            'reward_points': 15,
                            'explanation': 'Yes! Plants grow toward light because they need it to make food.'
                        }
                    ]
                },
                {
                    'order': 3,
                    'title': 'Growing Leaves',
                    'story_text': 'Your plant is getting bigger! Beautiful green leaves are opening up to catch the sunlight.',
                    'required_score_to_unlock': 35,
                    'questions': [
                        {
                            'order': 1,
                            'type': 'drag_drop',
                            'title': 'Match the plant parts to their functions',
                            'payload': {
                                'items': ['Leaves', 'Roots', 'Stem'],
                                'targets': ['Make food from sunlight', 'Drink water from soil', 'Support the plant'],
                                'matches': [[0, 0], [1, 1], [2, 2]]
                            },
                            'correct_answer': [[0, 0], [1, 1], [2, 2]],
                            'reward_points': 20
                        }
                    ]
                },
                {
                    'order': 4,
                    'title': 'Beautiful Flowers',
                    'story_text': 'Amazing! Your plant has grown colorful flowers that will attract bees and butterflies!',
                    'required_score_to_unlock': 60,
                    'questions': [
                        {
                            'order': 1,
                            'type': 'multiple_choice',
                            'title': 'Why do flowers have bright colors?',
                            'payload': {
                                'choices': ['To look pretty', 'To attract insects', 'To scare animals', 'No reason'],
                            },
                            'correct_answer': [1],
                            'reward_points': 25,
                            'explanation': 'Flowers have bright colors to attract bees and other insects that help plants make seeds!'
                        }
                    ]
                },
                {
                    'order': 5,
                    'title': 'Mighty Tree',
                    'story_text': 'Congratulations! Your tiny seed has grown into a mighty tree that will live for many years!',
                    'required_score_to_unlock': 90,
                    'questions': [
                        {
                            'order': 1,
                            'type': 'fill_blank',
                            'title': 'Trees give us fresh _____ to breathe.',
                            'payload': {
                                'sentence': 'Trees give us fresh _____ to breathe.',
                                'options': ['oxygen', 'water', 'food', 'light']
                            },
                            'correct_answer': 'oxygen',
                            'reward_points': 30,
                            'explanation': 'Trees make oxygen from carbon dioxide, giving us fresh air to breathe!'
                        }
                    ]
                }
            ]
        
        elif subject_slug == 'math':
            return [
                {
                    'order': 1,
                    'title': 'Base Camp - Counting',
                    'story_text': 'Welcome to Math Mountain! Let\'s start our climb by learning to count at base camp.',
                    'questions': [
                        {
                            'order': 1,
                            'type': 'multiple_choice',
                            'title': 'How many apples do you see?',
                            'payload': {
                                'choices': ['2', '3', '4', '5'],
                                'images': ['/media/images/three_apples.png']
                            },
                            'correct_answer': [1],
                            'reward_points': 10
                        },
                        {
                            'order': 2,
                            'type': 'drag_drop',
                            'title': 'Put the numbers in order',
                            'payload': {
                                'items': ['3', '1', '4', '2'],
                                'targets': ['First', 'Second', 'Third', 'Fourth'],
                                'matches': [[1, 0], [3, 1], [0, 2], [2, 3]]
                            },
                            'correct_answer': [[1, 0], [3, 1], [0, 2], [2, 3]],
                            'reward_points': 15
                        }
                    ]
                },
                {
                    'order': 2,
                    'title': 'First Checkpoint - Addition',
                    'story_text': 'Great job! Now let\'s learn to add numbers together as we climb higher.',
                    'required_score_to_unlock': 20,
                    'questions': [
                        {
                            'order': 1,
                            'type': 'multiple_choice',
                            'title': 'What is 2 + 3?',
                            'payload': {'choices': ['4', '5', '6', '7']},
                            'correct_answer': [1],
                            'reward_points': 15
                        }
                    ]
                },
                {
                    'order': 3,
                    'title': 'Mid Mountain - Shapes',
                    'story_text': 'Look at all the different shapes in the rocks around us! Let\'s learn about them.',
                    'required_score_to_unlock': 40,
                    'questions': [
                        {
                            'order': 1,
                            'type': 'image_choice',
                            'title': 'Which shape is a triangle?',
                            'payload': {
                                'images': [
                                    '/media/images/triangle.png',
                                    '/media/images/circle.png',
                                    '/media/images/square.png',
                                    '/media/images/rectangle.png'
                                ]
                            },
                            'correct_answer': [0],
                            'reward_points': 20
                        }
                    ]
                },
                {
                    'order': 4,
                    'title': 'High Peak - Subtraction',
                    'story_text': 'The air is getting thinner, but we\'re almost there! Let\'s practice subtraction.',
                    'required_score_to_unlock': 65,
                    'questions': [
                        {
                            'order': 1,
                            'type': 'multiple_choice',
                            'title': 'What is 10 - 4?',
                            'payload': {'choices': ['5', '6', '7', '8']},
                            'correct_answer': [1],
                            'reward_points': 25
                        }
                    ]
                },
                {
                    'order': 5,
                    'title': 'Summit Victory!',
                    'story_text': 'Congratulations! You\'ve reached the top of Math Mountain! You\'re a number champion!',
                    'required_score_to_unlock': 95,
                    'questions': [
                        {
                            'order': 1,
                            'type': 'multiple_choice',
                            'title': 'If you have 3 groups of 2 cookies, how many cookies total?',
                            'payload': {'choices': ['5', '6', '7', '8']},
                            'correct_answer': [1],
                            'reward_points': 30,
                            'explanation': '3 groups of 2 is the same as 2 + 2 + 2 = 6 cookies!'
                        }
                    ]
                }
            ]
        
        # Add similar data for language and general_knowledge subjects...
        else:
            # Default levels for other subjects
            return [
                {
                    'order': 1,
                    'title': f'{subject_slug.title()} Level 1',
                    'story_text': f'Welcome to {subject_slug.title()}! Let\'s start learning!',
                    'questions': [
                        {
                            'order': 1,
                            'type': 'multiple_choice',
                            'title': f'Sample {subject_slug} question',
                            'payload': {'choices': ['A', 'B', 'C', 'D']},
                            'correct_answer': [0],
                            'reward_points': 10
                        }
                    ]
                },
                {
                    'order': 2,
                    'title': f'{subject_slug.title()} Level 2',
                    'story_text': f'Great progress in {subject_slug.title()}! Let\'s continue!',
                    'required_score_to_unlock': 10,
                    'questions': [
                        {
                            'order': 1,
                            'type': 'true_false',
                            'title': f'Another {subject_slug} question',
                            'payload': {'statement': 'This is a sample statement'},
                            'correct_answer': True,
                            'reward_points': 15
                        }
                    ]
                }
            ]
    
    def _create_badges(self):
        """Create achievement badges."""
        self.stdout.write('Creating badges...')
        
        badges = [
            {
                'name': 'First Steps',
                'description': 'Complete your first level!',
                'badge_type': 'completion',
                'criteria': {'type': 'complete_levels', 'count': 1},
                'points_reward': 50,
                'rarity_level': 1
            },
            {
                'name': 'Science Explorer',
                'description': 'Complete all science levels!',
                'badge_type': 'completion',
                'criteria': {'type': 'complete_subject', 'subject': 'science'},
                'points_reward': 200,
                'rarity_level': 3
            },
            {
                'name': 'Math Master',
                'description': 'Complete all math levels!',
                'badge_type': 'completion',
                'criteria': {'type': 'complete_subject', 'subject': 'math'},
                'points_reward': 200,
                'rarity_level': 3
            },
            {
                'name': 'Perfect Score',
                'description': 'Get 100% on any level!',
                'badge_type': 'performance',
                'criteria': {'type': 'perfect_score', 'count': 1},
                'points_reward': 100,
                'rarity_level': 2
            },
            {
                'name': 'Speed Demon',
                'description': 'Complete a level in under 60 seconds!',
                'badge_type': 'performance',
                'criteria': {'type': 'fast_completion', 'time_limit': 60},
                'points_reward': 150,
                'rarity_level': 4
            },
            {
                'name': 'Week Warrior',
                'description': 'Play for 7 days in a row!',
                'badge_type': 'streak',
                'criteria': {'type': 'daily_streak', 'days': 7},
                'points_reward': 300,
                'rarity_level': 3
            },
            {
                'name': 'Ultimate Learner',
                'description': 'Complete all subjects with perfect scores!',
                'badge_type': 'special',
                'criteria': {'type': 'perfect_all_subjects'},
                'points_reward': 1000,
                'rarity_level': 5
            }
        ]
        
        for badge_data in badges:
            badge, created = Badge.objects.get_or_create(
                name=badge_data['name'],
                defaults=badge_data
            )
            if created:
                self.stdout.write(f'  Created badge: {badge.name}')