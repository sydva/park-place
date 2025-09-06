# Park Place Backend Architecture

## Project Overview
Park Place is a parking space marketplace app (think Airbnb for parking) with two user types:
- **Renters**: Find and book parking spaces
- **Listers**: Share their parking spaces for others to rent

## Current Frontend Analysis
The React frontend has these key components:
1. **Map View**: Shows parking spaces with location markers, prices, and ratings
2. **Add Parking Space**: Allows users to pin location, upload photos, add descriptions
3. **Report License Plate**: Feature for reporting issues
4. **User Menu**: Navigation and user actions

## Proposed Backend Architecture

### Tech Stack
- **FastAPI**: Modern async web framework with automatic OpenAPI docs
- **anyio**: Structured concurrency with asyncio ecosystem compatibility
- **SQLAlchemy**: ORM with async support
- **PostgreSQL**: Primary database
- **Redis**: Caching and session management
- **S3/MinIO**: Image storage

### Core Data Models

```python
# Users
- id, email, password_hash, name
- user_type (renter/lister/both)
- rating, verified, created_at
- car_license_plate (for renters)

# ParkingSpaces
- id, owner_id, lat, lng
- title, description, price_per_hour
- image_urls[], tags[]
- rating, is_available
- created_at, updated_at

# Bookings
- id, space_id, renter_id
- start_time, end_time
- total_price, status
- created_at

# Reviews
- id, booking_id, reviewer_id
- rating, comment
- created_at
```

### API Endpoints Structure

```
/api/v1/
├── auth/
│   ├── POST /register
│   ├── POST /login
│   ├── POST /logout
│   └── GET /me
├── spaces/
│   ├── GET / (search with filters)
│   ├── POST / (create new)
│   ├── GET /{id}
│   ├── PUT /{id}
│   ├── DELETE /{id}
│   └── POST /{id}/upload-image
├── bookings/
│   ├── GET /my-bookings
│   ├── POST /create
│   ├── PUT /{id}/cancel
│   └── GET /space/{space_id}
├── reviews/
│   ├── POST /
│   └── GET /space/{space_id}
└── users/
    ├── GET /profile/{id}
    └── PUT /profile
```

### Implementation Priorities (Hackathon Mode)

#### Phase 1: Core MVP (2-3 hours)
1. Basic FastAPI setup with anyio
2. Auth endpoints (simple JWT)
3. CRUD for parking spaces
4. Basic search/filter endpoint

#### Phase 2: Essential Features (2 hours)
1. Booking system
2. Image upload (local storage for now)
3. Basic availability checking

#### Phase 3: Nice-to-haves (if time permits)
1. Reviews/ratings
2. Real-time updates via WebSockets
3. Email notifications

### Quick Start Commands

```bash
# Install dependencies
uv pip install fastapi anyio sqlalchemy asyncpg python-jose passlib python-multipart

# Run development server
uvicorn backend.main:app --reload --port 8000

# Run with anyio
python -m backend.main
```

### Key Design Decisions

1. **anyio over pure asyncio**: Structured concurrency with compatibility for asyncio database libraries
2. **JWT auth**: Stateless, simple for hackathon
3. **PostgreSQL**: Robust geospatial queries with PostGIS extension
4. **Local file storage initially**: Skip S3 complexity for MVP

### Security Considerations
- Password hashing with bcrypt
- JWT tokens with short expiry
- Rate limiting on auth endpoints
- Input validation via Pydantic
- CORS configuration for frontend

### Performance Optimizations
- Database connection pooling
- Redis caching for hot queries
- Pagination on list endpoints
- Spatial indexing for location queries

## Next Steps
1. Set up project structure
2. Create database models
3. Implement auth system
4. Build core CRUD endpoints
5. Test with frontend integration