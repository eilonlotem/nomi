# Nomi - Inclusive Dating App

An inclusive dating app for people with disabilities, built with Vue 3 + Tailwind CSS (frontend) and Django REST Framework (backend).

## 🏗️ Project Structure

```
nomi/
├── frontend/          # Vue 3 + Tailwind CSS frontend
│   ├── src/
│   │   ├── App.vue
│   │   ├── composables/
│   │   ├── i18n/
│   │   └── style.css
│   ├── tests/         # Playwright E2E tests
│   ├── package.json
│   └── vite.config.js
│
├── backend/           # Django REST Framework backend
│   ├── config/        # Django settings
│   ├── users/         # User authentication
│   ├── profiles/      # User profiles & preferences
│   ├── matching/      # Swipes, matches, chat
│   ├── manage.py
│   └── requirements.txt
│
└── README.md
```

## ✨ Features

- **Multi-language Support**: English, Hebrew, Spanish, French, Arabic
- **RTL Support**: Full right-to-left layout for Hebrew and Arabic
- **Accessibility**: Large touch targets, high contrast, reduced motion options
- **Social Login**: Facebook and Instagram authentication (mock)
- **Profile Matching**: Swipe-based discovery with compatibility scoring
- **Chat**: Real-time messaging between matches
- **Identity Tags**: Disability and identity-based tags for better matches

## 🚀 Getting Started

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`

### Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed initial data
python manage.py seed_data

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

Backend runs at `http://localhost:8000`

### Running Both Together

For full functionality, run both frontend and backend simultaneously:

**Terminal 1 - Backend:**
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

The frontend automatically connects to the backend at `http://localhost:8000/api`. If the backend is unavailable, the app gracefully falls back to mock data.

### API Integration

The frontend uses composables and services for API communication:

- `useAuth()` - Authentication (login, logout, token validation)
- `useProfile()` - Profile management
- `useDiscovery()` - Swipe/discovery functionality
- `useMatches()` - Match management
- `useChat()` - Messaging

These can be imported from:
```javascript
import { useAuth } from './composables/useAuth'
import { useProfile, useDiscovery } from './composables/useApi'
import { profileApi, matchingApi, chatApi } from './services/api'
```

## 📱 API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/social-auth/` - Social login (Facebook/Instagram)
- `GET /api/auth/me/` - Get current user
- `POST /api/auth/language/` - Update preferred language

### Profiles
- `GET /api/profiles/tags/` - List disability tags
- `GET /api/profiles/interests/` - List interests
- `GET/PUT /api/profiles/me/` - Get/update my profile
- `POST /api/profiles/me/photos/` - Upload photo
- `POST /api/profiles/me/mood/` - Update current mood
- `GET/PUT /api/profiles/me/looking-for/` - Dating preferences

### Matching
- `GET /api/discover/` - Get profiles for discovery
- `POST /api/swipe/` - Record swipe action
- `GET /api/matches/` - List matches
- `GET /api/conversations/` - List conversations
- `GET/POST /api/conversations/{id}/messages/` - Messages

## 🧪 Testing

### Frontend E2E Tests (Playwright)

```bash
cd frontend

# Run all tests
npm test

# Run with UI
npm run test:ui

# Run headed (watch browser)
npm run test:headed

# Run specific browser
npm run test:chromium
npm run test:mobile
```

### Backend Tests

```bash
cd backend
source venv/bin/activate
pytest
```

## 🌐 Deployment

### Frontend (Vercel)

```bash
cd frontend
npx vercel --prod
```

### Backend

Set environment variables:
- `SECRET_KEY` - Django secret key
- `DEBUG=False` - Disable debug mode
- `ALLOWED_HOSTS` - Your domain(s)
- `CORS_ALLOWED_ORIGINS` - Frontend URL(s)
- `DATABASE_URL` - Production database (PostgreSQL)

## 📝 Environment Variables

### Frontend
Create a `.env` file in the `frontend/` directory:

```env
# Backend API URL
VITE_API_URL=http://localhost:8000/api

# Facebook App ID (get from Facebook Developer Console)
# Without this, the app uses mock login for development
VITE_FACEBOOK_APP_ID=your_facebook_app_id
```

### Backend
Create a `.env` file in the `backend/` directory:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
FRONTEND_URL=http://localhost:5173

# Facebook OAuth (from Facebook Developer Console)
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
```

## 🔐 Setting Up Facebook Login

1. Go to [Facebook Developers](https://developers.facebook.com/apps/)
2. Create a new app (Consumer type)
3. Add "Facebook Login" product
4. Configure OAuth settings:
   - Valid OAuth Redirect URIs: `http://localhost:5173`, `http://localhost:8000/social/complete/facebook/`
   - Enable "Login with JavaScript SDK"
   - Add your domain to "Allowed Domains for the JavaScript SDK"
5. Copy App ID and App Secret to your `.env` files
6. In App Settings > Basic, add `localhost` to App Domains

**Note:** For development without Facebook setup, the app uses mock login automatically.

## 🛠️ Tech Stack

### Frontend
- Vue 3 (Composition API)
- Tailwind CSS
- Vite
- Playwright (E2E testing)

### Backend
- Django 4.2
- Django REST Framework
- SQLite (dev) / PostgreSQL (prod)
- django-cors-headers

## 📄 License

MIT
