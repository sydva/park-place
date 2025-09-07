# Park Place - Parking Space Marketplace

## Setup

### Frontend
```bash
cd site && npm install && npm start
```

### Backend
```bash
cd backend && python main.py
```

## Google Places API Integration (Optional)

To import parking locations from Google Places:

1. Get a Google Places API key:
   - Go to [Google Cloud Console](https://console.developers.google.com/apis/credentials)
   - Create a new project or select existing one
   - Enable the Places API
   - Create credentials (API key)

2. Set up your API key:
   ```bash
   cd backend
   cp .env.example .env
   # Edit .env and add your API key
   ```

3. Import parking locations:
   ```bash
   cd backend
   # San Francisco (default)
   python import_google_places.py
   
   # Custom location (latitude, longitude, radius in meters)
   python import_google_places.py 40.7589 -73.9851 1000
   ```

This will populate your database with real parking locations from Google Places API.