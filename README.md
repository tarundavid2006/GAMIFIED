# Gamified Learning Platform

A complete offline-first learning platform for children aged 6-14, featuring gamified lessons in Math, Language, Science, and General Knowledge.

## 🚀 Quick Start

### Development Setup
```bash
# Clone and setup
git clone <your-repo-url>
cd gamified-learning-platform

# Backend setup
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data
python manage.py runserver

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

### Docker Setup (Recommended)
```bash
# One command to rule them all
docker-compose up --build
```

Access:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/
- Admin Panel: http://localhost:8000/admin/
- API Docs: http://localhost:8000/api/docs/

## 🎮 Features

### Core Features
- **Offline-First PWA**: Works completely offline after initial load
- **Multi-Avatar Support**: Share devices with siblings/classmates
- **Adventure Paths**: Story-driven learning for 4 subjects
- **Instant Rewards**: Lottie animations, badges, confetti
- **Accessibility**: Large touch targets, audio cues, ARIA support
- **Lightweight**: Optimized for low-end devices

### Learning Subjects
1. **Science** 🌱 - Plant growth adventure (sprout → tree)
2. **Math** ⛰️ - Mountain trail with checkpoint flags
3. **Language** 📚 - Storybook pages with illustrations
4. **General Knowledge** 🗺️ - World map with landmark stickers

### Technical Features
- Django + DRF backend with PostgreSQL
- React + Vite PWA frontend
- IndexedDB for offline storage
- Conflict-resilient sync
- Device-based profiles (no accounts needed)
- Automated testing suite

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Offline Testing
1. Open DevTools → Network tab
2. Set throttling to "Offline"
3. Refresh app - should work completely offline
4. Complete a level offline
5. Re-enable network - sync should happen automatically

## 📱 PWA Installation

1. Open app in Chrome/Edge
2. Look for "Install App" prompt
3. Or: Menu → "Install Gamified Learning Platform"

## 👥 Group Mode Testing

Simulate device sharing:
```bash
# Create test device profiles
cd backend
python manage.py shell
>>> from learning.models import DeviceProfile, Avatar
>>> DeviceProfile.objects.create(device_id="test_device_1", avatar_id=1)
>>> DeviceProfile.objects.create(device_id="test_device_2", avatar_id=2)
```

## 🔧 Development

### Adding New Content
1. Access admin panel: http://localhost:8000/admin/
2. Add subjects, levels, questions, and avatars
3. Upload Lottie animations as JSON
4. Content appears in app automatically

### Project Structure
```
gamified-learning-platform/
├── backend/                 # Django + DRF
│   ├── learning/           # Main app
│   ├── api/               # API endpoints
│   └── manage.py
├── frontend/              # React PWA
│   ├── src/
│   │   ├── components/    # UI components
│   │   ├── services/      # API & sync logic
│   │   ├── stores/        # Local storage
│   │   └── workers/       # Service worker
│   └── public/
├── docker-compose.yml
└── README.md
```

### API Endpoints
- `GET /api/subjects/` - List all subjects
- `GET /api/subjects/{slug}/levels/` - Get levels for subject
- `GET /api/levels/{id}/questions/` - Get questions for level
- `POST /api/device/profiles/` - Create/update device profile
- `PATCH /api/device/profiles/{device_id}/progress/` - Sync progress
- `GET /api/leaderboard/` - Get leaderboard data

## 🎨 Asset Guidelines

### Lottie Animations
- Keep under 200KB
- Use simple shapes and colors
- Test on mobile devices
- Include fallback static images

### Audio Files
- MP3 format, < 100KB per file
- Clear pronunciation for language content
- Positive, encouraging tones

## 🔐 Production Notes

### Adding Authentication (Future)
Current version uses device-based profiles. To add user accounts:

1. Add Django User model relationships
2. Implement JWT authentication
3. Update frontend to handle login/logout
4. Modify sync logic for user-based data

### Scaling Considerations
- Use Redis for caching frequent API calls
- Implement CDN for static assets
- Add database indexing for large datasets
- Consider horizontal scaling with load balancers

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📄 License

MIT License - see LICENSE file for details.

---

Built with ❤️ for young learners everywhere! 🎓✨