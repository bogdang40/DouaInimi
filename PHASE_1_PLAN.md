# Două Inimi - Romanian Christian Dating App

## 📋 Project Overview

**Project Name:** Două Inimi (Two Hearts)  
**Target:** Romanian Christians in USA & Canada  
**Scale:** ~1000 users  
**Stack:** Flask + SQLite (dev) / PostgreSQL (prod) + Azure  
**Domain:** 2inimi.com (Cloudflare)  
**GitHub:** https://github.com/bogdang40/DouaInimi.git  
**Live URL:** https://2inimi.com  
**Last Deploy:** December 29, 2025

---

## 🚀 DEPLOYMENT STATUS - LIVE ✅

### Azure Infrastructure ✅ Complete

| Service | Name | Region | Tier | Cost/Month | Status |
|---------|------|--------|------|------------|--------|
| **App Service** | douainimi | East US 2 | Basic B1 | ~$12 | ✅ Live |
| **PostgreSQL** | douainimi-db | Canada Central | Burstable B1ms | ~$17 | ✅ Connected |
| **Blob Storage** | douainimiphotos | East US | Standard LRS | ~$2 | ✅ Integrated |
| **Domain** | 2inimi.com | Cloudflare | - | ~$1 | ✅ Connected |
| **Email** | SendGrid | - | Free (100/day) | $0 | ✅ Configured |
| **GitHub Actions** | CI/CD | - | - | $0 | ✅ Auto-deploy |
| **Total** | | | | **~$32/month** | |

### App Service Environment Variables ✅ All Configured

| Variable | Value | Status |
|----------|-------|--------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ Set |
| `SECRET_KEY` | Random 64-char hex | ✅ Set |
| `FLASK_ENV` | `production` | ✅ Set |
| `AZURE_STORAGE_CONNECTION_STRING` | Blob storage connection | ✅ Set |
| `AZURE_STORAGE_CONTAINER` | `photos` | ✅ Set |
| `SENDGRID_API_KEY` | `SG.xxxxx...` | ✅ Set |
| `MAIL_FROM` | `noreply@2inimi.com` | ✅ Set |

### Service Details

**Database:**
```
Host: douainimi-db.postgres.database.azure.com
Database: postgres
Username: douainimiadmin
Port: 5432
```

**Blob Storage:**
```
Account: douainimiphotos
Container: photos
URL: https://douainimiphotos.blob.core.windows.net/photos/
```

**Email:**
```
Provider: SendGrid (Free tier - 100 emails/day)
From: noreply@2inimi.com
Routing: Cloudflare Email Routing → Your Gmail
```

**Domain:**
```
Domain: 2inimi.com
Registrar: Cloudflare
SSL: Cloudflare (free)
```

### ✅ DEPLOYMENT COMPLETE - All Steps Done

| # | Step | Status | Notes |
|---|------|--------|-------|
| 1 | **Code committed** | ✅ Complete | GitHub repo: bogdang40/DouaInimi |
| 2 | **GitHub Actions CI/CD** | ✅ Complete | Auto-deploys on push to `main` |
| 3 | **Database migrations** | ✅ Complete | Runs automatically on app startup |
| 4 | **Domain connected** | ✅ Complete | https://2inimi.com via Cloudflare |
| 5 | **SSL certificate** | ✅ Complete | Cloudflare free SSL |
| 6 | **Admin panel** | ✅ Complete | https://2inimi.com/admin |
| 7 | **Photo storage** | ✅ Complete | Azure Blob Storage integrated |
| 8 | **Email service** | ✅ Complete | SendGrid configured |

### 🔄 How Deployment Works Now

```bash
# Make changes locally
git add -A
git commit -m "Your change description"
git push origin main

# GitHub Actions automatically:
# 1. Builds the app
# 2. Deploys to Azure App Service
# 3. Runs database migrations on startup
# Wait ~3 minutes, then visit https://2inimi.com
```

---

## 📋 DETAILED DEPLOYMENT GUIDE

### 🚨 IMPORTANT: What Happens with PostgreSQL

The admin panel and all new features (passes tracking, reports, etc.) need database tables. Here's what you need to know:

**Tables that will be created on first `flask db upgrade`:**
- `users` - User accounts (with `is_approved` column for admin approval)
- `profiles` - User dating profiles
- `photos` - User photos
- `likes` - Like records
- `matches` - Mutual match records
- `messages` - Chat messages
- `blocks` - Block records
- `reports` - User reports (for admin review)
- `passes` - Pass/swipe-left tracking (NEW)

**The admin panel uses hardcoded credentials** (not in database), so no special admin user setup needed.

---

### Step 1: Commit All Changes
```bash
cd /Users/yztpp8/Desktop/Personal/Dating
git add -A
git commit -m "Add admin panel with user approvals, reports, analytics"
```

### Step 2: Push Code to GitHub
```bash
git push -u origin main
```
Use your GitHub credentials (bogdang40) when prompted.

### Step 3: Connect Azure to GitHub (If Not Already Done)
1. Go to [Azure Portal](https://portal.azure.com)
2. Open **App Service** → `douainimi`
3. Left menu → **Deployment Center**
4. Source: **GitHub**
5. Sign in and authorize Azure to access your GitHub
6. Organization: `bogdang40`
7. Repository: `DouaInimi`
8. Branch: `main`
9. Click **Save**

✅ Azure will auto-deploy whenever you push to GitHub!

### Step 4: Set Startup Command
1. App Service → **Configuration** → **General settings** tab
2. **Leave Startup Command EMPTY** - Let Azure auto-detect
   - Azure will automatically run: `gunicorn 'run:app'`
   - The `gunicorn.conf.py` file in the repo configures workers & threads
3. Click **Save**
4. Click **Restart** (top of page)

**Performance Configuration (gunicorn.conf.py):**
```python
# Automatically picked up by Gunicorn
workers = 2          # Number of worker processes
threads = 4          # Threads per worker (for Socket.IO)
timeout = 120        # Worker timeout
```

### Step 5: Run Database Migrations (CRITICAL)
After deployment completes (check Deployment Center for status):

1. App Service → **SSH** (under Development Tools, or use **Console**)
2. Run these commands:

```bash
# Navigate to app directory
cd /home/site/wwwroot

# Set environment variables (if not already set)
export FLASK_APP=run.py
export FLASK_ENV=production

# Install dependencies
pip install -r requirements.txt

# Run migrations - this creates all tables
flask db upgrade
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> xxxx, initial migration
INFO  [alembic.runtime.migration] Running upgrade xxxx -> yyyy, add reports columns
...
```

### Step 6: Create Passes Table (One-Time)
The `passes` table may not be in migrations yet. Run this in SSH:

```bash
cd /home/site/wwwroot
python << 'EOF'
from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    # Create all tables that don't exist
    db.create_all()
    print("✅ All tables created/verified!")
EOF
```

### Step 7: Verify Database Tables
Check that all tables exist:

```bash
cd /home/site/wwwroot
python << 'EOF'
from app import create_app
from app.extensions import db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("📦 Database Tables:")
    for table in sorted(tables):
        print(f"  ✓ {table}")
    
    required = ['users', 'profiles', 'photos', 'likes', 'matches', 'messages', 'blocks', 'reports', 'passes']
    missing = [t for t in required if t not in tables]
    if missing:
        print(f"\n⚠️ Missing tables: {missing}")
    else:
        print("\n✅ All required tables present!")
EOF
```

### Step 8: Connect Domain (2inimi.com)

**In Azure:**
1. App Service → **Custom domains**
2. Click **+ Add custom domain**
3. Domain: `2inimi.com`
4. Copy the verification TXT record value

**In Cloudflare DNS:**
| Type | Name | Content |
|------|------|---------|
| TXT | `asuid` | (paste Azure verification code) |
| CNAME | `@` | `douainimi.azurewebsites.net` |
| CNAME | `www` | `douainimi.azurewebsites.net` |

5. Back in Azure → Validate → Add

**SSL Certificate:**
- Cloudflare handles SSL automatically (set to "Full" mode in Cloudflare SSL/TLS settings)

### Step 9: Test Everything!

**Public Site:**
- [ ] Visit https://2inimi.com
- [ ] Register a new account
- [ ] Check email verification arrives (SendGrid)
- [ ] Complete profile
- [ ] Upload a photo (Azure Blob)
- [ ] Test messaging

**Admin Panel:**
- [ ] Visit https://2inimi.com/admin
- [ ] Login with: `gramisteanu40@gmail.com` / `Suceava$1`
- [ ] Check Dashboard loads with stats
- [ ] Test Approvals page
- [ ] Test Users page
- [ ] Test Reports page
- [ ] Test Analytics page

---

## 🔧 TROUBLESHOOTING

### "No module named 'app'" Error
```bash
cd /home/site/wwwroot
pip install -r requirements.txt
```

### "Table doesn't exist" Error
```bash
cd /home/site/wwwroot
flask db upgrade
# Then run db.create_all() script above
```

### Admin Login Not Working
Check the credentials match exactly:
- Email: `gramisteanu40@gmail.com`
- Password: `Suceava$1` (case-sensitive!)

### Photos Not Uploading
Check Azure Blob Storage connection string is set in App Service → Configuration:
- `AZURE_STORAGE_CONNECTION_STRING`
- `AZURE_STORAGE_CONTAINER` = `photos`

### Emails Not Sending
Check SendGrid API key is set:
- `SENDGRID_API_KEY`
- `MAIL_FROM` = `noreply@2inimi.com`

---

## 🔄 FUTURE DEPLOYMENTS

After initial setup, deployments are automatic:

```bash
# Make changes locally
git add -A
git commit -m "Your change description"
git push origin main
```

Azure will automatically:
1. Detect the push
2. Pull the code
3. Install dependencies
4. Restart the app

**If you add new database columns:**
1. Generate migration locally: `flask db migrate -m "description"`
2. Push to GitHub
3. SSH into Azure and run: `flask db upgrade`

---

## 🎯 Current Status: **LIVE IN PRODUCTION** 🚀

**Site:** https://2inimi.com  
**Admin:** https://2inimi.com/admin

### What's Been Built

| Feature | Status | Notes |
|---------|--------|-------|
| **Project Scaffold** | ✅ Complete | Flask app factory, blueprints, models |
| **Database Models** | ✅ Complete | User, Profile, Photo, Match, Like, Message, Report, Block |
| **Authentication** | ✅ Complete | Login, Register, Logout, Session management |
| **Profile System** | ✅ Complete | Create, Edit, View profiles with all fields |
| **Photo Upload** | ✅ Complete | Azure Blob storage, primary photo, max 6 photos |
| **Discover (Grid)** | ✅ Complete | Browse profiles with Like/Pass |
| **Discover (Swipe)** | ✅ Complete | Tinder-like card swiping interface |
| **Search & Filters** | ✅ Complete | Filter by denomination, location, language, etc. |
| **Matching System** | ✅ Complete | Mutual likes create matches, passes tracked, opposite-sex only |
| **Messaging** | ✅ Complete | Real-time chat with Socket.IO |
| **AJAX Messaging** | ✅ Complete | No page refresh, POST-Redirect-GET safe |
| **Typing Indicators** | ✅ Complete | Real-time "typing..." display |
| **Online Status** | ✅ Complete | Online now / Last active indicators |
| **Light/Dark Theme** | ✅ Complete | Toggle with persistence |
| **Admin Panel** | ✅ Complete | User management, reports, stats dashboard |
| **Admin Login** | ✅ Complete | Separate hardcoded credentials, session-based |
| **User Approvals** | ✅ Complete | Approve/reject new registrations |
| **User Management** | ✅ Complete | View, suspend, verify, premium, delete users |
| **Reports Dashboard** | ✅ Complete | Pending/resolved reports, admin actions |
| **Flagged Content** | ✅ Complete | Users with pending reports for review |
| **Analytics** | ✅ Complete | 30-day charts: signups, messages, matches |
| **Height Units** | ✅ Complete | Toggle between cm and ft/in in profile |
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

## 🔐 Admin Panel

### Access
- **URL:** `/admin` (or `/admin/login`)
- **Separate login** from user authentication
- **Hardcoded credentials** in `app/routes/admin.py`

### Current Admin Credentials
```python
ADMIN_CREDENTIALS = {
    'gramisteanu40@gmail.com': 'Suceava$1',
}
```

### Features
| Feature | URL | Description |
|---------|-----|-------------|
| Dashboard | `/admin/` | Stats overview, quick actions, recent signups |
| Approvals | `/admin/approvals` | Approve/reject new user registrations |
| Users | `/admin/users` | Search, filter, manage all users |
| User Detail | `/admin/users/<id>` | Full user info, suspend/verify/delete |
| Reports | `/admin/reports` | View and resolve user reports |
| Flagged | `/admin/flagged` | Auto-flagged content for review |
| Analytics | `/admin/analytics` | 30-day charts for signups/messages/matches |
| Settings | `/admin/settings` | System info, quick links |

### Adding New Admins
Edit `app/routes/admin.py` and add to the `ADMIN_CREDENTIALS` dict:
```python
ADMIN_CREDENTIALS = {
    'gramisteanu40@gmail.com': 'Suceava$1',
    'another@admin.com': 'SecurePassword123',
}
```

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
| **Storage** | Azure Blob Storage (with local fallback) |

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

### ✅ Production Features Complete

| Feature | Priority | Status | Description |
|---------|----------|--------|-------------|
| **Azure Blob Storage** | 🔴 High | ✅ Complete | Photos stored in Azure, persists across deploys |
| **SendGrid Email** | 🔴 High | ✅ Complete | Email verification, password reset working |
| **Database Migrations** | 🔴 High | ✅ Complete | Auto-run on app startup |
| **Pass Tracking** | 🔴 High | ✅ Complete | Users you pass don't reappear in swipe |

### 🔮 Future Enhancements (Optional)

| Feature | Priority | Complexity | Description |
|---------|----------|------------|-------------|
| **reCAPTCHA** | 🟡 Medium | Low | Bot protection (code ready, needs keys) |
| **Profile Boost** | 🟢 Low | Medium | Premium feature |
| **Stripe Payments** | 🟢 Low | High | Premium subscriptions |
| **Push Notifications** | 🟢 Low | Medium | Browser push for matches/messages |
| **Mobile App Build** | 🟢 Low | High | Capacitor iOS/Android builds |

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

### Infrastructure Status ✅

| Task | Priority | Status |
|------|----------|--------|
| Azure App Service | 🔴 High | ✅ Live (Basic B1, Linux, East US 2) |
| Azure PostgreSQL | 🔴 High | ✅ Connected (Burstable B1ms, Canada Central) |
| Azure Blob Storage | 🔴 High | ✅ Integrated (code uploads photos automatically) |
| App Service Config | 🔴 High | ✅ All 7 env vars set |
| Domain | 🔴 High | ✅ 2inimi.com via Cloudflare |
| SSL Certificate | 🔴 High | ✅ Cloudflare free SSL |
| SendGrid Email | 🔴 High | ✅ Verified sender, emails working |
| GitHub CI/CD | 🔴 High | ✅ Auto-deploy on push to main |
| Database Migrations | 🔴 High | ✅ Auto-run on app startup |
| reCAPTCHA | 🟢 Low | ⏳ Optional (code ready) |
| Sentry monitoring | 🟢 Low | ⏳ Optional |
| Azure CDN | 🟢 Low | ⏳ Optional |

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

## 💰 Azure Cost (Actual)

| Service | Tier | Actual Cost |
|---------|------|-------------|
| App Service | Basic B1 (1 core, 1.75GB) | **$12.41/month** |
| PostgreSQL | Burstable B1ms (1 vCore, 2GB RAM, 32GB) | **$17.56/month** |
| Blob Storage | Standard LRS | ~$2/month |
| SendGrid | Free tier (100 emails/day) | $0 |
| Domain | 2inimi.com (Cloudflare) | ~$10/year |
| **Current Total** | | **~$32/month** |

---

## 🌐 Domain Setup (2inimi.com)

### Connect Domain to Azure App Service

1. **In Azure App Service** → Custom domains
2. Click **+ Add custom domain**
3. Enter: `2inimi.com` and `www.2inimi.com`
4. Azure will show you DNS records to add

### Add DNS Records in Cloudflare

1. Go to Cloudflare → DNS
2. Add these records:

| Type | Name | Content | Proxy |
|------|------|---------|-------|
| CNAME | `@` | `douainimi.azurewebsites.net` | Proxied (orange) |
| CNAME | `www` | `douainimi.azurewebsites.net` | Proxied (orange) |
| TXT | `asuid` | (Azure verification code) | DNS only |

3. Wait ~5 minutes for propagation
4. Validate in Azure

### SSL Certificate
- Cloudflare provides **free SSL** when proxy is enabled
- Azure also has free managed certificates for custom domains

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

1. ~~Email sending not configured~~ ✅ Fixed - SendGrid integrated
2. ~~Photos stored locally~~ ✅ Fixed - Azure Blob Storage integrated
3. ~~No rate limiting yet~~ ✅ Fixed
4. No reCAPTCHA on registration (optional, code ready)
5. ~~Report UI needs user-facing form~~ ✅ Fixed
6. Generate PNG icons from SVG for all sizes

---

## 🎯 Immediate Next Steps (Complete Deployment)

### ✅ COMPLETED
- [x] Azure App Service created (Basic B1, ~$12/month)
- [x] Azure PostgreSQL created (Burstable B1ms, ~$17/month)
- [x] Environment variables configured (DATABASE_URL, SECRET_KEY, FLASK_ENV)
- [x] Code committed to git (104 files)
- [x] GitHub repository created: https://github.com/bogdang40/DouaInimi.git

### ⏳ REMAINING (Do These Now)

#### Step 1: Push Code to GitHub
```bash
cd /Users/yztpp8/Desktop/Personal/Dating
git push -u origin main
```
(Use your GitHub credentials when prompted)

#### Step 2: Connect Azure to GitHub
1. Go to Azure App Service → **Deployment Center**
2. Source: **GitHub**
3. Authorize and select `bogdang40/DouaInimi`
4. Branch: `main`
5. Save

#### Step 3: Add Startup Command
1. App Service → **Configuration** → **General settings**
2. **Leave Startup Command EMPTY** - Let Azure auto-detect
3. The `gunicorn.conf.py` file configures: 2 workers, 4 threads each
4. Save

#### Step 4: Run Database Migrations
After deployment completes:
1. App Service → **SSH** (under Development Tools)
2. Run:
```bash
cd /home/site/wwwroot
flask db upgrade
```

#### Step 5: Test Live Site
- Visit: `https://douainimi.azurewebsites.net`

### 🔮 FUTURE ENHANCEMENTS (After Launch)
- [ ] Add reCAPTCHA keys (bot protection)
- [ ] Add Sentry (error monitoring)
- [ ] Azure CDN for faster image loading
- [ ] Profile Boost (premium feature)
- [ ] Stripe payments integration
- [ ] Push notifications (web push)
- [ ] Mobile app (Capacitor build)

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

## 📅 Deployment Timeline

| Date | Milestone |
|------|-----------|
| Dec 2024 | Phase 1 Development Complete |
| Dec 27, 2024 | Azure Infrastructure Created |
| Dec 27, 2024 | App Service + PostgreSQL configured |
| Dec 28, 2024 | GitHub CI/CD setup, first deployment |
| Dec 28, 2024 | Domain connected (2inimi.com) |
| Dec 29, 2024 | Admin panel fixed, Azure Blob integrated |
| **Dec 29, 2024** | **🚀 LIVE at https://2inimi.com** |

---

## ✅ VALIDATION CHECKLIST

### Core Functionality (Test These)

| Feature | URL | Status |
|---------|-----|--------|
| Homepage | https://2inimi.com | ✅ Working |
| User Registration | https://2inimi.com/auth/register | ⏳ Test |
| User Login | https://2inimi.com/auth/login | ⏳ Test |
| Email Verification | Check email after register | ⏳ Test |
| Profile Creation | After login → profile setup | ⏳ Test |
| **Photo Upload** | Profile → Photos | ⏳ **Validate Azure Blob** |
| Discover/Swipe | https://2inimi.com/discover/swipe | ⏳ Test |
| Pass Tracking | Pass user → shouldn't reappear | ✅ Fixed |
| Matches | Like mutual → creates match | ⏳ Test |
| Messaging | Click match → chat | ⏳ Test |

### Admin Panel (Test These)

| Feature | URL | Status |
|---------|-----|--------|
| Admin Login | https://2inimi.com/admin | ✅ Working |
| Dashboard | https://2inimi.com/admin/ | ✅ Working |
| Approvals | https://2inimi.com/admin/approvals | ⏳ Test |
| Users | https://2inimi.com/admin/users | ✅ Working |
| Reports | https://2inimi.com/admin/reports | ✅ Working |
| Flagged | https://2inimi.com/admin/flagged | ✅ Fixed |
| Analytics | https://2inimi.com/admin/analytics | ✅ Working |
| Settings | https://2inimi.com/admin/settings | ⏳ Test |

### Photo Storage Validation

**IMPORTANT: Enable Anonymous Blob Access (One-Time Setup)**

The Azure Blob container is set to "Private" by default. For photos to display, you have two options:

**Option A: Enable Public Access (Recommended for dating app)**
1. Go to **Azure Portal** → Storage Account `douainimiphotos`
2. Click **Configuration** (left menu)
3. Set **"Allow Blob anonymous access"** to **Enabled**
4. Click **Save**
5. Go to **Containers** → `photos`
6. Click **Change access level**
7. Select **"Blob (anonymous read access for blobs only)"**
8. Click **OK**

**Option B: Use SAS Tokens (Already Implemented)**
- New photo uploads automatically include SAS tokens (signed URLs)
- Existing photos uploaded before this fix need re-upload or Option A

**To verify Azure Blob Storage is working:**
1. **Login to the app** at https://2inimi.com
2. **Go to Profile → Photos**
3. **Delete your old photo** (if any - it has no SAS token)
4. **Upload a NEW test photo**
5. The photo should display immediately
6. **Check Azure Portal** → Storage Account `douainimiphotos` → Container `photos`
7. **Verify the photo file appears** in the container

If photos show `/static/uploads/...` instead, Azure Blob Storage isn't connected. Check:
- `AZURE_STORAGE_CONNECTION_STRING` env var is set in Azure App Service
- `AZURE_STORAGE_CONTAINER` = `photos`

### Email Validation

To verify SendGrid is working:

1. **Register a new test account** at https://2inimi.com/auth/register
2. **Check your email** for verification email from `noreply@2inimi.com`
3. **Click the verification link**

If no email arrives, check:
- `SENDGRID_API_KEY` env var is set
- `MAIL_FROM` = `noreply@2inimi.com`
- SendGrid sender verification is complete

---

## 🔑 Quick Reference

### Local Development
```bash
cd /Users/yztpp8/Desktop/Personal/Dating
source venv/bin/activate
python run.py
# → http://localhost:5001
```

### Deploy to Azure
```bash
git add .
git commit -m "Your changes"
git push origin main
# Azure auto-deploys from GitHub
```

### Azure Resources
- **Live URL:** https://2inimi.com (after domain setup)
- **Azure URL:** douainimi.azurewebsites.net
- **PostgreSQL:** douainimi-db.postgres.database.azure.com
- **Blob Storage:** douainimiphotos.blob.core.windows.net (after setup)
- **Resource Group:** DouaInimi
- **Region:** East US 2 (App), Canada Central (DB)

---

**Status:** Phase 1 Complete ✅ | Deploying to Production 🚀
