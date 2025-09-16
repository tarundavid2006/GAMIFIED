# Testing & Demo Guide

## 🧪 Complete Testing Workflow

### Quick Start (Docker - Recommended)

```bash
# One command to start everything
docker-compose up --build

# Wait for containers to start, then visit:
# - Frontend: http://localhost:5173
# - Backend API: http://localhost:8000/api/
# - Admin Panel: http://localhost:8000/admin/
# - API Docs: http://localhost:8000/api/docs/
```

### Development Setup

#### Backend Setup
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac  
source venv/bin/activate

pip install -r requirements.txt

# Setup database
python manage.py migrate
python manage.py seed_data
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## 🎯 Testing Checklist

### ✅ PWA & Offline Functionality

1. **PWA Installation**
   - Open Chrome/Edge → `http://localhost:5173`
   - Look for "Install App" prompt or Menu → Install
   - App should install as standalone PWA

2. **Offline Mode Testing**
   - Open DevTools → Network tab
   - Set throttling to "Offline" 
   - Refresh app - should work completely offline
   - Complete a level offline
   - Re-enable network - sync should happen automatically

3. **Service Worker Verification**
   - DevTools → Application → Service Workers
   - Should show active service worker
   - Cache storage should contain app assets

### ✅ Core Learning Features

1. **Avatar Selection**
   - First run should show avatar selection
   - 4 avatars: Mango, Luna, Rocket, Coral
   - Audio cues and animations work
   - Selection persists across sessions

2. **Subject Navigation**
   - 4 subjects with adventure themes:
     - 🌱 Science (Plant Growth)
     - ⛰️ Math (Mountain Trail)  
     - 📚 Language (Storybook)
     - 🗺️ General Knowledge (World Map)

3. **Level Progression**
   - Levels unlock based on previous completion
   - Progress indicators show completion status
   - Story text appears before each level
   - Visual progression (seed → plant, base camp → summit, etc.)

4. **Question Interface**
   - Multiple choice questions with large tap targets
   - Instant feedback with animations
   - Audio cues for correct/incorrect answers
   - Points awarded immediately

### ✅ Device Sharing & Group Mode

1. **Multi-Profile Support**
   ```bash
   # Test multiple profiles on same device
   # Switch between avatars in Profile tab
   # Each avatar maintains separate progress
   ```

2. **Progress Isolation**
   - Each avatar has independent progress
   - Switching avatars shows different completion states
   - Local storage keys separate by avatar

### ✅ Rewards System

1. **Instant Feedback**
   - Confetti animation on correct answers
   - Lottie animations for badge unlocks
   - Audio celebrations

2. **Badges & Achievements**
   - "First Steps" - Complete first level
   - "Science Explorer" - Complete all science levels
   - "Perfect Score" - Get 100% on any level
   - Check Rewards tab for earned badges

3. **Leaderboard**
   - Shows points per avatar/device
   - Local rankings (offline)
   - Server-side rankings (when online)

### ✅ API Endpoints Testing

#### Core Endpoints
```bash
# List all subjects
GET http://localhost:8000/api/subjects/

# Get subject levels  
GET http://localhost:8000/api/subjects/science/levels/

# Get level with questions (for offline caching)
GET http://localhost:8000/api/levels/1/

# List avatars
GET http://localhost:8000/api/avatars/

# Create device profile
POST http://localhost:8000/api/device/profiles/
{
  "device_id": "test_device_123",
  "avatar_id": 1,
  "progress_data": {"total_points": 0}
}

# Sync progress
PATCH http://localhost:8000/api/device/profiles/test_device_123/progress/
{
  "progress_entries": [{
    "level_id": 1,
    "score": 85,
    "attempts": 2,
    "completion_time": 120
  }],
  "version": 1,
  "last_updated": "2024-01-15T12:00:00Z"
}

# Get leaderboard
GET http://localhost:8000/api/leaderboard/?limit=10

# Health check
GET http://localhost:8000/api/health/
```

### ✅ Admin Interface Testing

1. **Access Admin**
   - Visit: http://localhost:8000/admin/
   - Use superuser credentials created earlier

2. **Content Management**
   - Add new subjects, levels, questions
   - Upload Lottie animations (JSON format)
   - Create new avatars and badges
   - View device profiles and progress data

3. **Sample Data Verification**
   - Should see 4 subjects with 5 levels each
   - 4 avatars with sample animations
   - 7 achievement badges
   - Questions with various types (MCQ, T/F, drag-drop)

### ✅ Accessibility Testing

1. **Keyboard Navigation**
   - Tab through all interactive elements
   - Enter/Space to activate buttons
   - Focus indicators should be visible

2. **Screen Reader Support**
   - ARIA labels on interactive elements
   - Alt text for images
   - Semantic HTML structure

3. **Large Touch Targets**
   - All buttons minimum 44px size
   - Easy to tap on mobile devices
   - Adequate spacing between elements

4. **Color Contrast**
   - High contrast mode support
   - Text readable on all backgrounds
   - Color not the only indicator

## 🎬 Demo Video Suggestions

### 5-Minute Demo Flow

1. **App Launch (30s)**
   - Show PWA installation prompt
   - First-time avatar selection
   - Brief UI tour

2. **Learning Experience (2 min)**
   - Navigate to Science subject
   - Complete "Plant a Seed" level
   - Show question interactions and feedback
   - Demonstrate progress tracking

3. **Offline Capabilities (1 min)**
   - Enable airplane mode/offline
   - Show app still works
   - Complete another level
   - Re-enable network and show sync

4. **Group Mode & Rewards (1 min)**
   - Switch to different avatar
   - Show separate progress
   - Complete level to earn badge
   - Show confetti and rewards screen

5. **Admin & API (30s)**
   - Quick tour of admin interface
   - Show API documentation
   - Highlight content management features

### Screen Recording Tips

- Use 1920x1080 resolution
- Record at 30 FPS
- Include device simulation for mobile view
- Add voice narration explaining key features
- Show browser DevTools for offline testing
- Highlight child-friendly UI elements

### Key Selling Points to Highlight

- ✨ **Works completely offline** - No internet required after initial load
- 🎮 **Gamified learning** - Adventure themes make learning fun
- 👥 **Device sharing** - Perfect for families and classrooms  
- 🎨 **Kid-friendly UI** - Large buttons, animations, audio cues
- 📱 **PWA technology** - Install like native app
- 🔄 **Smart sync** - Conflict-resistant progress synchronization
- ♿ **Accessible design** - Works for all children
- 📊 **Progress tracking** - Detailed learning analytics

## 🐛 Common Issues & Solutions

### Backend Issues
```bash
# Database not migrated
python manage.py migrate

# No sample data
python manage.py seed_data --reset

# Missing dependencies
pip install -r requirements.txt

# CORS errors
# Check CORS_ALLOWED_ORIGINS in settings.py
```

### Frontend Issues
```bash
# Dependencies not installed
npm install

# Build errors
npm run build

# PWA not working
# Check service worker registration in DevTools
# Verify manifest.json is accessible

# Offline mode not working
# Clear browser cache
# Re-register service worker
```

### Docker Issues
```bash
# Containers not starting
docker-compose down
docker-compose up --build

# Database connection errors
# Wait for db container to be healthy
# Check DATABASE_URL environment variable

# Port conflicts
# Change ports in docker-compose.yml if 5173/8000 are taken
```

## 🚀 Production Deployment Notes

### Environment Variables
```bash
# Backend (.env)
SECRET_KEY=your-secret-key
DEBUG=False
DATABASE_URL=postgres://user:pass@host:port/dbname
ALLOWED_HOSTS=yourdomain.com

# Frontend (.env)
VITE_API_BASE_URL=https://your-api-domain.com
```

### Performance Optimization
- Enable Django's `DEBUG=False`
- Use CDN for static assets
- Implement Redis caching
- Add database indexing
- Compress images and animations
- Minify JavaScript/CSS

### Security Considerations
- Use HTTPS in production
- Implement rate limiting
- Add input validation
- Secure file uploads
- Use environment variables for secrets

---

Built with ❤️ for young learners everywhere! 🎓✨