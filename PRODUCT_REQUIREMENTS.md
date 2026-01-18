# Nomi - Product Requirements Document

## Mission Statement

Nomi is an **inclusive dating app specifically designed for people with disabilities**, built with accessibility as a core principle. Our goal is to create a safe, welcoming space where users can connect authentically, celebrate their identities, and find meaningful relationships.

---

## Core Features

### 1. Authentication
- **Social Login**: Facebook and Instagram OAuth integration
- **JWT Token-based Auth**: Secure session management
- **Language Preference**: Set preferred language during onboarding
- **Onboarding Flow**: Guided setup for new users

### 2. User Profiles

| Field | Description |
|-------|-------------|
| Display Name | User's preferred name |
| Bio | Up to 500 characters |
| Date of Birth | For age calculation and matching |
| Gender | Male, Female, Non-binary, Other, Prefer not to say |
| Photos | Multiple photos with primary selection |
| Location | City, country, and coordinates for distance matching |
| Disability Tags | Selectable identity/disability tags (localized) |
| Interests | Categorized interests for matching |
| Current Mood | Energy level: Low Energy, Open to Connect, Ready to Chat, Feeling Bold |
| Profile Prompts | Conversation starters (e.g., "The thing that makes me laugh most is...") |
| Ask Me About It | Celebration prompts about disability/difference |
| Time Preferences | Preferred times for dates (morning, afternoon, evening, night, flexible) |
| Response Pace | Quick, Moderate, Slow, Variable |
| Dating Pace | Ready to meet, Prefer to chat first, Virtual dates preferred, Flexible |

### 3. Discovery & Matching

#### Swipe Actions
- **Pass**: Not interested
- **Like**: Interested
- **Super Like**: Very interested (highlighted to recipient)

#### Matching Algorithm
Compatibility scoring uses weighted factors:

| Factor | Weight | Description |
|--------|--------|-------------|
| Shared Disability Tags | 20% | Common identity/disability experiences |
| Shared Interests | 15% | Overlapping hobbies and interests |
| Distance | 15% | Geographic proximity |
| Age Compatibility | 10% | Within preferred age range |
| Gender Match | 10% | Matches gender preferences |
| Relationship Type | 10% | Looking for same type (casual, serious, friends, activity partners) |
| Mood Compatibility | 8% | Compatible energy levels |
| Pace Compatibility | 7% | Similar response and dating pace |
| Time Preferences | 5% | Overlapping availability |

#### Filtering Criteria
- Gender preferences (mutual match required)
- Age preferences (mutual match required)
- Maximum distance preference

### 4. Chat & Messaging

| Feature | Description |
|---------|-------------|
| Text Messages | Standard text communication |
| Voice Notes | Audio messages with duration tracking |
| Images | Photo sharing in conversations |
| Icebreakers | Pre-written conversation starters |
| Read Receipts | Message read status with timestamp |
| Conversations | One conversation per match |

### 5. Safety Features

#### Block & Report
- **Block**: Prevent user from contacting you
- **Report Reasons**: Spam, Inappropriate Content, Harassment, Fake Profile, Other
- **Description**: Optional details about the report

---

## Accessibility Requirements

### Multi-language Support
- English (en)
- Hebrew (he)
- Spanish (es)
- French (fr)
- Arabic (ar)

### RTL Support
- Full right-to-left layout for Hebrew and Arabic
- Proper text alignment and UI mirroring

### Accessibility Features
- Large touch targets (minimum 44x44px)
- High contrast mode support
- Reduced motion option
- Screen reader compatibility
- Semantic HTML structure
- ARIA labels where needed

---

## Dating Preferences (Looking For)

| Preference | Options |
|------------|---------|
| Genders | Men, Women, Non-binary, Everyone |
| Relationship Types | Casual Dating, Serious Relationship, Just Friends, Activity Partners |
| Age Range | Min age to Max age (default: 18-50) |
| Max Distance | In kilometers (default: 50km) |
| Preferred Location | Text description |

---

## API Endpoints

### Authentication
```
POST /api/auth/register/        - Register new user
POST /api/auth/social-auth/     - Social login (Facebook/Instagram)
GET  /api/auth/me/              - Get current user
POST /api/auth/language/        - Update preferred language
```

### Profiles
```
GET  /api/profiles/tags/        - List disability tags
GET  /api/profiles/interests/   - List interests
GET  /api/profiles/me/          - Get my profile
PUT  /api/profiles/me/          - Update my profile
POST /api/profiles/me/photos/   - Upload photo
POST /api/profiles/me/mood/     - Update current mood
GET  /api/profiles/me/looking-for/  - Get dating preferences
PUT  /api/profiles/me/looking-for/  - Update dating preferences
```

### Matching
```
GET  /api/discover/             - Get profiles for discovery
POST /api/swipe/                - Record swipe action
GET  /api/matches/              - List matches
```

### Conversations
```
GET  /api/conversations/              - List conversations
GET  /api/conversations/{id}/         - Get conversation details
GET  /api/conversations/{id}/messages/ - Get messages
POST /api/conversations/{id}/messages/ - Send message
```

---

## Tech Stack

### Frontend
- **Framework**: Vue 3 (Composition API)
- **Styling**: Tailwind CSS
- **Build Tool**: Vite
- **Testing**: Playwright (E2E)
- **Deployment**: Vercel

### Backend
- **Framework**: Django 4.2 + Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: JWT + Social Auth
- **Deployment**: Render

---

## Data Models

### Core Entities
1. **User** - Authentication and account data
2. **Profile** - Extended user profile information
3. **ProfilePhoto** - User photos
4. **DisabilityTag** - Predefined identity/disability tags
5. **Interest** - Predefined interests
6. **LookingFor** - Dating preferences
7. **Swipe** - User swipe actions
8. **Match** - Mutual matches between users
9. **Conversation** - Chat threads
10. **Message** - Individual messages
11. **Block** - Block/report records

---

## User Flows

### Onboarding
1. Login via Facebook/Instagram
2. Language selection (Hebrew default)
3. Profile setup (name, bio, photos)
4. Disability/identity tags selection
5. Dating preferences configuration
6. Discovery screen

### Discovery
1. View potential match cards
2. Swipe left (pass) or right (like) or up (super like)
3. On mutual like → Match created → Chat enabled

### Matching
1. Both users like each other
2. Compatibility score calculated
3. Match record created
4. Conversation automatically created
5. Users can start messaging

---

## Success Metrics

- User registration and onboarding completion rate
- Daily active users
- Swipe activity rate
- Match rate (mutual likes / total likes)
- Message response rate
- User retention (7-day, 30-day)
- Accessibility compliance score

---

*Last Updated: January 2026*
