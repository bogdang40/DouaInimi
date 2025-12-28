# Două Inimi - Mobile App Deployment Guide

This guide covers how to deploy your PWA as native iOS and Android apps.

## Option 1: PWA (Recommended for MVP)

Your app is already a Progressive Web App (PWA) that can be installed directly from the browser.

### Benefits
- ✅ No app store approval needed
- ✅ Instant updates (no app store review)
- ✅ Works offline
- ✅ Push notifications (with user permission)
- ✅ Home screen icon
- ✅ Full-screen experience

### Testing PWA
1. Open your site on mobile (must be HTTPS)
2. Look for "Add to Home Screen" prompt
3. Or manually: Share → Add to Home Screen

### PWA Requirements (Already Implemented)
- [x] `manifest.json` with app metadata
- [x] Service worker for offline support
- [x] HTTPS deployment
- [x] Responsive mobile design
- [x] Touch-optimized UI
- [x] Safe area handling (iPhone notch)

---

## Option 2: Native Apps with Capacitor

For App Store / Play Store distribution, use Capacitor to wrap your PWA.

### Prerequisites
```bash
# Install Node.js 18+
# Install Xcode (macOS, for iOS)
# Install Android Studio (for Android)
```

### Setup Capacitor

```bash
# Navigate to project root
cd /Users/yztpp8/Desktop/Personal/Dating

# Install Capacitor
npm init -y
npm install @capacitor/core @capacitor/cli
npm install @capacitor/ios @capacitor/android

# Initialize Capacitor (already configured in mobile/capacitor.config.json)
npx cap init "Două Inimi" "com.douainimi.app" --web-dir=app/static

# Add platforms
npx cap add ios
npx cap add android
```

### Configure for Production

1. **Update `mobile/capacitor.config.json`:**
   - Set `server.url` to your production domain
   - Remove `server` block entirely for bundled app

2. **For bundled app (no server):**
```json
{
  "appId": "com.douainimi.app",
  "appName": "Două Inimi",
  "webDir": "web-build"
}
```

### Build & Deploy

#### iOS (requires macOS + Xcode)
```bash
# Sync web assets
npx cap sync ios

# Open in Xcode
npx cap open ios

# In Xcode:
# 1. Set your Team in Signing & Capabilities
# 2. Set Bundle Identifier
# 3. Archive for distribution
```

#### Android
```bash
# Sync web assets
npx cap sync android

# Open in Android Studio
npx cap open android

# In Android Studio:
# 1. Update version in build.gradle
# 2. Generate signed APK/AAB
```

### Push Notifications

Install push notification plugin:
```bash
npm install @capacitor/push-notifications
npx cap sync
```

Configure in your app:
```javascript
import { PushNotifications } from '@capacitor/push-notifications';

// Request permission
const result = await PushNotifications.requestPermissions();
if (result.receive === 'granted') {
    await PushNotifications.register();
}

// Get token
PushNotifications.addListener('registration', (token) => {
    console.log('Push token:', token.value);
    // Send to your server
});
```

---

## Option 3: PWABuilder (Easiest)

Use Microsoft's PWABuilder to generate store-ready packages.

### Steps
1. Go to https://www.pwabuilder.com/
2. Enter your deployed URL
3. Review your PWA score
4. Click "Package for stores"
5. Download iOS/Android packages
6. Upload to App Store Connect / Google Play Console

### Benefits
- No code changes needed
- Handles signing and packaging
- Generates store metadata

---

## App Store Submission Checklist

### iOS (App Store)
- [ ] Apple Developer Account ($99/year)
- [ ] App icons (1024x1024 required)
- [ ] Screenshots (6.5", 5.5", iPad)
- [ ] Privacy policy URL
- [ ] App description (4000 chars max)
- [ ] Keywords (100 chars)
- [ ] Support URL
- [ ] Age rating questionnaire
- [ ] Export compliance declaration

### Android (Google Play)
- [ ] Google Play Developer Account ($25 one-time)
- [ ] App icons (512x512 required)
- [ ] Feature graphic (1024x500)
- [ ] Screenshots (phone, tablet)
- [ ] Privacy policy URL
- [ ] App description (4000 chars max)
- [ ] Content rating questionnaire
- [ ] Data safety form

---

## Icon Generation

Generate all required icons from your SVG:

```bash
# Install ImageMagick
brew install imagemagick

# Generate PNG icons from SVG
cd app/static/icons

# iOS icons
convert icon-192x192.svg -resize 180x180 apple-touch-icon.png
convert icon-192x192.svg -resize 1024x1024 icon-1024x1024.png

# Android icons
for size in 36 48 72 96 144 192 512; do
  convert icon-192x192.svg -resize ${size}x${size} icon-${size}x${size}.png
done
```

Or use https://realfavicongenerator.net/ for complete favicon set.

---

## Recommended Plugins for Native Apps

```bash
# Essential plugins
npm install @capacitor/app          # App lifecycle
npm install @capacitor/haptics      # Vibration feedback
npm install @capacitor/keyboard     # Keyboard events
npm install @capacitor/status-bar   # Status bar control
npm install @capacitor/splash-screen # Splash screen

# Optional but nice
npm install @capacitor/share        # Native share sheet
npm install @capacitor/camera       # Camera access
npm install @capacitor/filesystem   # File access
```

---

## Testing

### iOS Simulator
```bash
npx cap run ios --target "iPhone 15 Pro"
```

### Android Emulator
```bash
npx cap run android --target "Pixel_7_API_34"
```

### Physical Device
```bash
# iOS - requires device connected and Xcode setup
npx cap run ios --device

# Android - requires USB debugging enabled
npx cap run android --device
```

---

## Performance Tips

1. **Optimize images** - Use WebP format, lazy loading
2. **Cache aggressively** - Service worker handles this
3. **Minimize JS** - Your current setup is already lean
4. **Use native features** - Haptics, share sheet feel better
5. **Test on real devices** - Emulators hide performance issues

---

## Support

For issues with:
- **Capacitor**: https://capacitorjs.com/docs
- **PWABuilder**: https://docs.pwabuilder.com/
- **App Store**: https://developer.apple.com/help/app-store-connect/
- **Play Console**: https://support.google.com/googleplay/android-developer/

