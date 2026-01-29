# MyFolio - Stock Trading Coach App

A mobile app that provides personalized trading insights based on your watchlist, powered by the After-Market Report analysis engine.

## Features

### Free Tier
- **5 Ticker Watchlist** - Track up to 5 stocks
- **Basic Coach Summary** - Daily market regime and key insights
- **Market Regime Indicator** - Risk-On / Risk-Off / Transitional status

### Pro Tier ($9.99/month or $79.99/year)
- **50 Ticker Watchlist** - Track up to 50 stocks
- **Full Coach Summary** - Detailed analysis with actionable items
- **Conviction Scores** - 1-5 scoring with emoji indicators (🔥✅⚠️🚫)
- **Pivot Levels** - Support and resistance levels for each ticker
- **Push Notifications** - Alerts for high-conviction setups
- **Daily Reports** - Full after-market reports
- **30 Days History** - Access to historical analysis

## Tech Stack

- **Frontend**: Expo / React Native
- **State Management**: React Context + AsyncStorage
- **Backend**: Firebase (Auth + Firestore)
- **Analysis API**: Python Flask server (connects to After-Market Report engine)
- **Navigation**: React Navigation (Bottom Tabs + Stack)

## Project Structure

```
myfolio-app/
├── App.tsx                     # Main app entry with navigation
├── src/
│   ├── config/
│   │   ├── firebase.ts         # Firebase initialization
│   │   ├── api.ts              # API endpoints and types
│   │   └── pricing.ts          # Pricing tiers and features
│   ├── context/
│   │   ├── AuthContext.tsx     # Authentication state
│   │   └── WatchlistContext.tsx # Watchlist management
│   ├── services/
│   │   └── api.ts              # API client and mock data
│   ├── screens/
│   │   ├── HomeScreen.tsx      # Dashboard with coach summary
│   │   ├── WatchlistScreen.tsx # Manage watchlist
│   │   ├── CoachScreen.tsx     # Detailed coach analysis
│   │   └── PricingScreen.tsx   # Subscription management
│   ├── components/             # Reusable UI components
│   ├── hooks/                  # Custom React hooks
│   └── utils/                  # Helper functions
├── assets/                     # Images and fonts
├── app.json                    # Expo configuration
└── package.json                # Dependencies
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn
- Expo CLI (`npm install -g expo-cli`)
- Firebase project (for authentication)

### Setup

1. **Install dependencies**
   ```bash
   cd myfolio-app
   npm install
   ```

2. **Configure Firebase**
   - Create a Firebase project at https://console.firebase.google.com
   - Enable Email/Password authentication
   - Create a Firestore database
   - Copy your config to `.env`:
   ```bash
   cp .env.example .env
   # Edit .env with your Firebase credentials
   ```

3. **Start the API server** (from parent directory)
   ```bash
   cd ..
   pip install flask flask-cors
   python api_server.py
   ```

4. **Run the app**
   ```bash
   cd myfolio-app
   npx expo start
   ```

5. **Open on device**
   - Scan QR code with Expo Go app (iOS/Android)
   - Or press `i` for iOS simulator / `a` for Android emulator

## API Endpoints

The app connects to a Python Flask backend:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/market/regime` | GET | Current market regime |
| `/api/market/macro` | GET | Macro data (SPY, VIX, etc.) |
| `/api/ticker/:symbol` | GET | Single ticker analysis |
| `/api/coach/summary` | POST | Coach summary for watchlist |
| `/api/report/generate` | POST | Generate full report (Pro) |

## Conviction Score System

| Score | Emoji | Meaning |
|-------|-------|---------|
| 4.5 - 5.0 | 🔥 | High conviction - strong setup |
| 3.5 - 4.4 | ✅ | Good setup - favorable risk/reward |
| 2.5 - 3.4 | ⚠️ | Caution - mixed signals |
| < 2.5 | 🚫 | Avoid - unfavorable conditions |

## Development

### Adding New Screens

1. Create screen component in `src/screens/`
2. Add to navigation in `App.tsx`
3. Update types if needed

### Connecting Real Data

Replace mock data in `src/services/api.ts` with actual API calls:

```typescript
// Change from:
setCoachSummary(mockCoachSummary);

// To:
const summary = await apiClient.getCoachSummary(watchlist.map(t => t.symbol));
setCoachSummary(summary);
```

## Building for Production

```bash
# Build for iOS
eas build --platform ios

# Build for Android
eas build --platform android
```

## License

MIT
