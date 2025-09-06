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
2. CRUD for parking spaces
3. Basic search/filter endpoint
4. Simple dev user (no auth for demo)

#### Phase 2: Essential Features (2 hours)
1. Booking system
2. Image upload (local storage)
3. Basic availability checking
4. License plate reporting endpoints

#### Phase 3: Nice-to-haves (if time permits)
1. Reviews/ratings
2. Real-time updates via WebSockets
3. Enhanced search filters

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
2. **No auth for hackathon**: Using hardcoded dev user for simplicity
3. **SQLite for MVP**: Simple setup, can migrate to PostgreSQL later
4. **Local file storage**: Skip S3 complexity for MVP

### Security Considerations (Post-Hackathon)
- Add proper authentication after demo
- Password hashing with bcrypt
- JWT tokens implementation
- Input validation via Pydantic (already implemented)
- CORS configuration for frontend (already implemented)

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

## Testing Tips

### Environment Setup
- Always use the `.venv` virtual environment: `source .venv/bin/activate`
- Install dependencies with uv: `uv pip install -r requirements.txt`
- Don't use system Python or other environments
- Check active environment with: `which pytest` (should show `.venv/bin/pytest`)

### Port Management
- Test scripts automatically find available ports
- Don't kill existing servers - tests use fresh ports each time
- Multiple test runs can happen simultaneously without conflicts

### Running Tests

#### Pytest Tests (server starts automatically)
```bash
# Activate environment first (if not already active)
source .venv/bin/activate

# Install dependencies
uv pip install -r requirements.txt

# Run all tests (server starts automatically)
pytest backend/tests/

# Run specific test file
pytest backend/tests/test_basic.py -v
```

#### Schemathesis CLI Tests
```bash
# Run all Schemathesis tests (starts/stops server automatically)
./backend/tests/run_schemathesis.sh

# Or manually:
# In terminal 1: Start the server
uvicorn backend.main:app --reload

# In terminal 2: Run Schemathesis
schemathesis run http://localhost:8000/openapi.json

# Or run the Python CLI test script
python backend/tests/test_cli_schemathesis.py
```

## Development Tips

* NEVER write defensive code, or work around errors.  We should crash early and often.
* After you've written some code, do a second editing pass to make it concise and idiomatic.  For example, minimal use of comments.
* Run pre-commit checks after each edit, to check that it's in good shape.
* **ALWAYS use Pydantic for validation** - Never validate in endpoint methods. All validation should be done via Pydantic models using Field constraints, validators, or Annotated types. This ensures validation rules appear in the OpenAPI schema and are properly documented.
