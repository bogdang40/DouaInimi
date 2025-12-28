# Două Inimi - Romanian Christian Dating App

## 📋 Project Overview

**Project Name:** Două Inimi (Two Hearts)  
**Target:** Romanian Christians in USA & Canada  
**Scale:** ~1000 users  
**Stack:** Flask + SQLite (dev) / PostgreSQL (prod) + Azure  

---

## 🎯 Current Status: **Phase 1 COMPLETE** ✅

### What's Been Built

| Feature | Status | Notes |
|---------|--------|-------|
| **Project Scaffold** | ✅ Complete | Flask app factory, blueprints, models |
| **Database Models** | ✅ Complete | User, Profile, Photo, Match, Like, Message, Report, Block |
| **Authentication** | ✅ Complete | Login, Register, Logout, Session management |
| **Profile System** | ✅ Complete | Create, Edit, View profiles with all fields |
| **Photo Upload** | ✅ Complete | Local storage, primary photo, max 6 photos |
| **Discover (Grid)** | ✅ Complete | Browse profiles with Like/Pass |
| **Discover (Swipe)** | ✅ Complete | Tinder-like card swiping interface |
| **Search & Filters** | ✅ Complete | Filter by denomination, location, language, etc. |
| **Matching System** | ✅ Complete | Mutual likes create matches |
| **Messaging** | ✅ Complete | Real-time chat with Socket.IO |
| **AJAX Messaging** | ✅ Complete | No page refresh, POST-Redirect-GET safe |
| **Typing Indicators** | ✅ Complete | Real-time "typing..." display |
| **Online Status** | ✅ Complete | Online now / Last active indicators |
| **Light/Dark Theme** | ✅ Complete | Toggle with persistence |
| **Admin Panel** | ✅ Complete | User management, reports, stats dashboard |
| **Profile Completion** | ✅ Complete | Progress bar and prompts |
| **Unread Badge** | ✅ Complete | Message count in navbar |
| **Conservative Fields** | ✅ Complete | Head covering, fasting, prayer frequency, etc. |
| **Multi-denomination** | ✅ Complete | Orthodox, Catholic, Baptist, Pentecostal, etc. |
| **Email Verification** | ✅ Complete | Token-based verification flow |
| **Password Reset** | ✅ Complete | Secure token-based password reset |
| **Report User** | ✅ Complete | Report form with reasons and block option |
| **Block User** | ✅ Complete | Block/unblock users, blocked users list |
| **Rate Limiting** | ✅ Complete | Flask-Limiter on auth routes |
| **Email Templates** | ✅ Complete | HTML + text templates for verification/reset |
| **Safety Routes** | ✅ Complete | `/safety/report`, `/safety/block`, `/safety/blocked` |
| **Security Module** | ✅ Complete | Input sanitization, spam detection, logging |
| **Security Headers** | ✅ Complete | CSP, X-Frame-Options, XSS Protection, etc. |
| **PWA Support** | ✅ Complete | Manifest, service worker, offline support |
| **Mobile Optimization** | ✅ Complete | Safe areas, touch targets, iOS keyboard |
| **Native App Ready** | ✅ Complete | Capacitor config, deployment guide |

---

## 🏗️ Architecture Summary

### Tech Stack (Current)

| Layer | Technology |
|-------|------------|
| **Backend** | Flask 3.x, Flask-Login, Flask-SocketIO, Flask-WTF |
| **Database** | SQLite (dev), PostgreSQL (prod ready) |
| **ORM** | SQLAlchemy + Flask-Migrate |
| **Frontend** | Jinja2, Tailwind CSS (CDN), Lucide Icons |
| **Real-time** | Socket.IO (typing, messages) |
| **Auth** | Flask-Login + Flask-Bcrypt |
| **Storage** | Local filesystem (Azure Blob ready) |

### Project Structure

```
dating-app/
├── app/
│   ├── __init__.py              # App factory with blueprints + security headers
│   ├── config.py                # Configuration (app name, choices)
│   ├── extensions.py            # Flask extensions
│   ├── utils/
│   │   ├── security.py          # Input sanitization, validation, spam detection
│   │   ├── image.py             # Image compression, EXIF fix, thumbnails
│   │   ├── moderation.py        # Profile/content auto-moderation
│   │   ├── recaptcha.py         # reCAPTCHA verification
│   │   └── notifications.py     # Push notification payloads
│   ├── services/
│   │   ├── email.py             # Email sending service
│   │   └── notification_emails.py  # Match/message email templates
│   ├── models/                  # SQLAlchemy models
│   │   ├── user.py              # User with online status
│   │   ├── profile.py           # Profile with conservative fields
│   │   ├── photo.py             # Photo management
│   │   ├── match.py             # Match & Like models
│   │   ├── message.py           # Messages with read status
│   │   └── report.py            # Report & Block models
│   ├── routes/
│   │   ├── main.py              # Landing, Dashboard, About, Terms, Offline
│   │   ├── auth.py              # Login, Register, Logout, Verify, Reset
│   │   ├── profile.py           # Profile CRUD, Photos
│   │   ├── discover.py          # Browse, Swipe, Search, Like/Pass
│   │   ├── matches.py           # Match list
│   │   ├── messages.py          # Inbox, Conversation, Socket events (secured)
│   │   ├── settings.py          # Account settings
│   │   ├── safety.py            # Report, Block, Blocked list
│   │   └── admin.py             # Admin panel
│   ├── templates/               # Jinja2 templates
│   │   ├── base.html            # PWA meta, Light/Dark theme, security
│   │   ├── components/          # Navbar, Flash, Profile Card
│   │   ├── admin/               # Dashboard, Users, Reports
│   │   └── ...                  # Auth, Profile, Discover, etc.
│   ├── forms/                   # WTForms
│   └── static/
│       ├── manifest.json        # PWA manifest
│       ├── sw.js                # Service worker for offline
│       ├── icons/               # App icons (multiple sizes)
│       └── ...                  # CSS, JS, Images
├── mobile/
│   └── capacitor.config.json    # Native app config (iOS/Android)
├── migrations/                  # Alembic migrations
├── seed_test_data.py           # 4 test users with data
├── run.py                       # Dev server
├── MOBILE_APP_GUIDE.md         # iOS/Android deployment guide
└── requirements.txt
```

---

## 📊 Feature Details

### User Features

| Feature | Description | Location |
|---------|-------------|----------|
| **Registration** | Email/password with validation | `/auth/register` |
| **Login** | Session-based with remember me | `/auth/login` |
| **Profile Edit** | All fields including conservative values | `/profile/edit` |
| **Photo Management** | Upload, delete, set primary | `/profile/photos` |
| **Discover Grid** | Grid view with filters link | `/discover` |
| **Discover Swipe** | Tinder-like cards with gestures | `/discover/swipe` |
| **Search** | Filter by denomination, location, etc. | `/discover/search` |
| **Matches** | List of mutual likes | `/matches` |
| **Messages** | Real-time chat with desktop sidebars | `/messages/<id>` |
| **Settings** | Theme toggle, account options | `/settings` |

### Admin Features

| Feature | Description | Location |
|---------|-------------|----------|
| **Dashboard** | Stats, charts, recent activity | `/admin` |
| **User Management** | Search, filter, view details | `/admin/users` |
| **User Actions** | Suspend, verify, premium, admin, delete | `/admin/users/<id>` |
| **Report Management** | View, resolve, dismiss reports | `/admin/reports` |
| **Report Actions** | Warn, suspend, ban users | `/admin/reports/<id>` |

### Profile Fields

**Basic Info:**
- First name, Last name, Date of birth, Gender
- City, State/Province, Country (US/CA)

**Romanian Heritage:**
- Origin region (Transilvania, Moldova, Muntenia, etc.)
- Romanian language ability (Fluent, Conversational, Learning, Heritage)
- Years in North America

**Faith & Church:**
- Denomination (11 options)
- Church name, Attendance frequency
- Faith importance

**Conservative/Traditional Values:**
- Conservatism level (Very Traditional → Modern)
- Head covering (Batic always, Church only, Pamblica, Sometimes, None)
- Fasting practice (Strict → None)
- Prayer frequency, Bible reading
- Family role views
- Same denomination spouse preference
- Church wedding preference

**Lifestyle:**
- Has children, Wants children
- Smoking, Drinking
- Height, Occupation, Education

**Preferences:**
- Looking for gender, Age range
- Relationship goal

---

## 🎨 UI/UX Features

### Theme System
- **Dark Mode:** Rose-to-purple gradient, glassmorphism, Cormorant Garamond font
- **Light Mode:** Clean white backgrounds, warm accents
- **Toggle:** Navbar icon, saves to localStorage
- **System Preference:** Respects `prefers-color-scheme`

### Real-time Features
- **Typing Indicators:** Animated dots, auto-timeout
- **Online Status:** Green badge on profile cards, chat header
- **Message Updates:** Socket.IO for instant delivery
- **Unread Badge:** Navbar message count

### Mobile Experience
- **Bottom Navigation:** Mobile-friendly nav bar
- **Touch Gestures:** Swipe cards with drag support + haptic feedback
- **Responsive:** All pages work on mobile
- **PWA Ready:** Service worker, manifest, install prompt
- **Safe Areas:** iPhone notch/dynamic island support
- **iOS Keyboard:** Proper handling, no zoom on focus
- **Offline Support:** Cached assets, offline page

### PWA / Native App Deployment
- **Progressive Web App:** Full PWA with service worker
- **iOS Home Screen:** Add to home screen support
- **Capacitor Ready:** Config for native iOS/Android builds
- **App Store Guide:** `MOBILE_APP_GUIDE.md` with deployment instructions

---

## 🧪 Test Data

4 test users created with `seed_test_data.py`:

| Email | Password | Gender | City | Denomination |
|-------|----------|--------|------|--------------|
| `test1@example.com` | `Test123!` | Female | Chicago | Orthodox |
| `test2@example.com` | `Test123!` | Male | Toronto | Baptist |
| `test3@example.com` | `Test123!` | Female | Los Angeles | Catholic |
| `test4@example.com` | `Test123!` | Male | New York | Pentecostal |

**Note:** `test1@example.com` is set as admin.

---

## 🚀 What's Next: Phase 2 - Production Ready

### ✅ Recently Built Features

| Feature | Status | Description |
|---------|--------|-------------|
| **Image Compression** | ✅ Complete | Pillow resize/compress on upload, EXIF fix, thumbnails |
| **Read Receipts** | ✅ Complete | Double checkmark for read messages |
| **Super Likes** | ✅ Complete | 3/day limit, special animation, match priority |
| **Push Notifications** | ✅ Complete | Browser notifications for matches/messages |
| **Email Notifications** | ✅ Complete | Beautiful HTML emails for matches/messages |
| **Profile Moderation** | ✅ Complete | Auto-flag suspicious content, spam detection |
| **reCAPTCHA** | ✅ Complete | Bot protection on registration (v2/v3 ready) |

### Remaining for Production

| Feature | Priority | Complexity | Description |
|---------|----------|------------|-------------|
| **Azure Blob Storage** | 🔴 High | Medium | Production photo storage |
| **SendGrid API Key** | 🔴 High | Low | Connect email service (code ready) |
| **reCAPTCHA Keys** | 🔴 High | Low | Get keys from Google (code ready) |
| **Profile Boost** | 🟢 Low | Medium | Premium feature |

### ✅ Recently Completed (This Session)

| Feature | Description |
|---------|-------------|
| **Email Verification Flow** | Token-based verification with HTML/text email templates |
| **Password Reset Flow** | Secure token-based reset with 1-hour expiry |
| **Report User Form** | Full form with reasons, description, auto-block option |
| **Block User System** | Block/unblock from profile, blocked users management |
| **Rate Limiting** | Flask-Limiter on login, register, forgot password |
| **Safety Blueprint** | Dedicated routes for report/block functionality |
| **Email Templates** | Beautiful responsive HTML email templates |
| **Verification Pending Page** | Friendly page explaining email verification |

### Infrastructure for Production

| Task | Priority | Status |
|------|----------|--------|
| Azure App Service setup | 🔴 High | Pending |
| Azure PostgreSQL setup | 🔴 High | Pending |
| Azure Blob Storage setup | 🔴 High | Pending |
| Custom domain + SSL | 🔴 High | Pending |
| SendGrid email setup | 🔴 High | Pending |
| GitHub Actions CI/CD | 🟡 Medium | Pending |
| Sentry error monitoring | 🟡 Medium | Pending |
| Azure CDN for images | 🟢 Low | Pending |

### Security Enhancements

| Task | Priority | Status |
|------|----------|--------|
| Rate limiting (Flask-Limiter) | ✅ Complete | 10/min login, 5/min register |
| CSRF on all forms | ✅ Complete | Flask-WTF |
| SQL injection prevention | ✅ Complete | SQLAlchemy ORM |
| XSS prevention | ✅ Complete | Jinja2 auto-escaping + JS escapeHtml |
| Report/Block system | ✅ Complete | Full UI + admin review |
| Security headers | ✅ Complete | CSP, X-Frame-Options, HSTS |
| Message sanitization | ✅ Complete | HTML stripping, spam detection |
| Socket.IO auth checks | ✅ Complete | Room access validation |
| Input validation module | ✅ Complete | `app/utils/security.py` |
| reCAPTCHA on registration | ✅ Complete | Code ready, needs keys |
| Content moderation | ✅ Complete | Auto-flag spam patterns |

---

## 📧 Email & reCAPTCHA Setup Guide

### SendGrid Setup (Email)

**Why SendGrid?** Free tier with 100 emails/day, reliable delivery, easy setup.

#### Step 1: Create SendGrid Account
1. Go to [sendgrid.com](https://sendgrid.com) and sign up (free tier available)
2. Complete email verification

#### Step 2: Domain Authentication (Recommended)
For professional emails (e.g., `noreply@douainimi.com`), you need a domain:

**Option A: Use Your Own Domain**
1. In SendGrid → Settings → Sender Authentication → Domain Authentication
2. Add your domain (e.g., `douainimi.com`)
3. Add the DNS records SendGrid provides to your domain:
   - 3 CNAME records for DKIM authentication
   - 1 TXT record for SPF
4. Wait for DNS propagation (up to 48h, usually 15min)

**Option B: Use Single Sender (Quick Start)**
1. Settings → Sender Authentication → Single Sender Verification
2. Verify a personal email as sender (e.g., `yourname@gmail.com`)
3. Good for testing, but may land in spam folders

**Recommended Domain Registrars:**
- [Namecheap](https://namecheap.com) - ~$10/year for `.com`
- [Porkbun](https://porkbun.com) - Often cheapest
- [Cloudflare](https://cloudflare.com) - At-cost pricing

#### Step 3: Get API Key
1. SendGrid → Settings → API Keys
2. Create API Key → Full Access (or restrict to Mail Send)
3. Copy the key (shown only once!)

#### Step 4: Configure App
Add to your `.env` file:
```bash
SENDGRID_API_KEY=SG.xxxxxxxxxxxxxxxxxx
MAIL_FROM=noreply@yourdomain.com
```

---

### reCAPTCHA Setup (Bot Protection)

**Why reCAPTCHA?** Prevents bot registrations and spam.

#### Step 1: Get Keys
1. Go to [Google reCAPTCHA Admin](https://www.google.com/recaptcha/admin)
2. Sign in with Google account
3. Register a new site:
   - **Label:** "Două Inimi Dating App"
   - **reCAPTCHA type:** v2 "I'm not a robot" (recommended) or v3 (invisible)
   - **Domains:** `localhost`, `yourdomain.com`, `yourapp.azurewebsites.net`
4. Copy **Site Key** and **Secret Key**

#### Step 2: Configure App
Add to your `.env` file:
```bash
RECAPTCHA_SITE_KEY=6LcXXXXXXXXXXXXXXXXXXXXXXX
RECAPTCHA_SECRET_KEY=6LcXXXXXXXXXXXXXXXXXXXXXXX
RECAPTCHA_TYPE=v2  # or v3
```

#### reCAPTCHA v2 vs v3
| Feature | v2 | v3 |
|---------|----|----|
| User sees | "I'm not a robot" checkbox | Nothing (invisible) |
| Best for | Registration forms | All forms |
| Accuracy | Very high | Scores 0-1 |
| Recommended | ✅ Start here | After launch |

---

### Azure Blob Storage Setup

#### Step 1: Create Storage Account
1. Azure Portal → Create Storage Account
2. Settings:
   - **Resource Group:** your-dating-app-rg
   - **Name:** douainimiphotos (unique)
   - **Region:** Same as App Service
   - **Performance:** Standard
   - **Redundancy:** LRS (cheapest)

#### Step 2: Create Container
1. Storage Account → Containers → + Container
2. Name: `photos`
3. Access level: Private (app will generate SAS URLs)

#### Step 3: Get Connection String
1. Storage Account → Access Keys
2. Copy Connection String

#### Step 4: Configure App
```bash
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=xxx;AccountKey=xxx;...
AZURE_STORAGE_CONTAINER=photos
```

---

## 🔐 Environment Variables Checklist

Create `.env` file in project root:

```bash
# Flask
SECRET_KEY=your-super-secret-key-change-this
FLASK_ENV=production  # or development
APP_NAME=Două Inimi
APP_URL=https://yourdomain.com

# Database (Production)
DATABASE_URL=postgresql://user:pass@server:5432/dbname

# Email (SendGrid)
SENDGRID_API_KEY=SG.xxxxxxxxxx
MAIL_FROM=noreply@yourdomain.com

# reCAPTCHA (optional but recommended)
RECAPTCHA_SITE_KEY=6LcXXXXXXXXXXXXXXXXXXXXXXX
RECAPTCHA_SECRET_KEY=6LcXXXXXXXXXXXXXXXXXXXXXXX

# Azure Blob Storage (for photos)
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;...
AZURE_STORAGE_CONTAINER=photos
```

---

## 💰 Azure Cost Estimate (Monthly)

| Service | Tier | Est. Cost |
|---------|------|-----------|
| App Service | B1 (1 core, 1.75GB) | ~$13 |
| PostgreSQL Flexible | Burstable B1ms | ~$15 |
| Blob Storage | 10GB + transactions | ~$2 |
| SendGrid | Free tier (100/day) | $0 |
| **Total** | | **~$30/month** |

---

## ✅ Phase 1 Completion Checklist

### Core Setup
- [x] Flask project structure
- [x] SQLAlchemy models (all)
- [x] Flask-Migrate configured
- [x] Database schema complete
- [x] Development environment
- [x] Environment variables

### Authentication
- [x] Registration form
- [x] Login/Logout
- [x] Session management
- [x] Protected routes
- [x] Email verification
- [x] Password reset
- [x] Rate limiting on auth routes

### Profile System
- [x] Profile creation
- [x] Profile edit page
- [x] Photo upload (local)
- [x] Photo management
- [x] Profile completion tracking
- [x] Conservative/Traditional fields

### Discovery & Matching
- [x] Browse profiles (grid)
- [x] Browse profiles (swipe)
- [x] Search with filters
- [x] Like/Pass system
- [x] Matching logic
- [x] Match notifications (flash)

### Messaging
- [x] Message inbox
- [x] Conversation view
- [x] Real-time with Socket.IO
- [x] Typing indicators
- [x] AJAX message sending
- [x] Read status

### UI/UX
- [x] Base template (dark/light)
- [x] Navigation components
- [x] Landing page
- [x] Dashboard with prompts
- [x] Profile view page
- [x] Settings page
- [x] Flash messages
- [x] Mobile responsive

### Admin
- [x] Admin dashboard
- [x] User management
- [x] Report management
- [x] User actions (suspend, verify, etc.)

---

## 🔧 Running the App

```bash
# Navigate to project
cd /Users/yztpp8/Desktop/Personal/Dating

# Activate virtual environment
source venv/bin/activate

# Run development server
python run.py

# Server runs at http://localhost:5001
```

### Seeding Test Data

```bash
python seed_test_data.py
```

### Database Migrations

```bash
# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

---

## 📝 Development Notes

### Key Design Decisions

1. **Flask over Django** - Simpler, less overhead, perfect for small apps
2. **Server-side rendering** - SEO-friendly, less JS complexity
3. **Socket.IO for real-time** - Typing indicators, instant messages
4. **Local storage first** - Easy dev, Azure Blob ready for prod
5. **Dark theme default** - Modern, elegant aesthetic
6. **Conservative fields** - Serves traditional community values

### Known Issues / TODOs

1. Email sending not configured (needs SendGrid API key)
2. Photos stored locally (need Azure Blob for prod)
3. ~~No rate limiting yet~~ ✅ Fixed
4. No reCAPTCHA on registration (optional)
5. ~~Report UI needs user-facing form~~ ✅ Fixed
6. Generate PNG icons from SVG for all sizes

---

## 🎯 Immediate Next Steps (Production Deployment)

1. **Azure Setup**
   - Create App Service (Linux B1)
   - Create PostgreSQL Flexible Server
   - Create Blob Storage account
   - Configure environment variables

2. **SendGrid Integration**
   - Create SendGrid account
   - Configure MAIL settings
   - Test email delivery

3. **Image Processing**
   - Add Pillow image resize on upload
   - Generate thumbnails
   - Compress large images

4. **Final Testing**
   - Test all user flows
   - Test admin panel
   - Test on mobile devices

---

## 📱 App URLs Summary

| Page | URL | Description |
|------|-----|-------------|
| Landing | `/` | Public homepage |
| Register | `/auth/register` | New user signup |
| Login | `/auth/login` | User login |
| Dashboard | `/dashboard` | User home |
| Discover (Grid) | `/discover` | Browse profiles |
| Discover (Swipe) | `/discover/swipe` | Tinder-style |
| Search | `/discover/search` | Filter profiles |
| Profile | `/profile` | Own profile |
| Edit Profile | `/profile/edit` | Edit profile |
| Photos | `/profile/photos` | Manage photos |
| Matches | `/matches` | Match list |
| Messages | `/messages` | Inbox |
| Conversation | `/messages/<id>` | Chat |
| Settings | `/settings` | Account settings |
| Blocked Users | `/safety/blocked` | Blocked list |
| Admin | `/admin` | Admin dashboard |
| Admin Users | `/admin/users` | User management |
| Admin Reports | `/admin/reports` | Report review |

---

## 🔐 Test Accounts

| Email | Password | Role |
|-------|----------|------|
| `test1@example.com` | `Test123!` | Admin |
| `test2@example.com` | `Test123!` | User |
| `test3@example.com` | `Test123!` | User |
| `test4@example.com` | `Test123!` | User |

---

Ready to deploy! 🚀
