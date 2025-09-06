from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

# Pydantic models for API requests/responses
class ParkingSpaceCreate(BaseModel):
    latitude: float
    longitude: float
    description: Optional[str] = None
    tags: List[str] = []
    image_url: Optional[str] = None

class ParkingSpaceResponse(BaseModel):
    id: str
    owner_id: str
    latitude: float
    longitude: float
    description: Optional[str] = None
    tags: List[str] = []
    image_url: Optional[str] = None
    created_at: datetime
    is_available: bool = True

class UserProfile(BaseModel):
    user_id: str
    email: str
    license_plate: Optional[str] = None
    rating: float = 0.0
    created_at: datetime

# In-memory storage for demo purposes
# In production, replace with proper database (PostgreSQL, etc.)
parking_spaces_db = {}
user_profiles_db = {}

def create_parking_space(user_id: str, space_data: ParkingSpaceCreate) -> ParkingSpaceResponse:
    """Create a new parking space"""
    import uuid
    space_id = str(uuid.uuid4())
    
    parking_space = ParkingSpaceResponse(
        id=space_id,
        owner_id=user_id,
        latitude=space_data.latitude,
        longitude=space_data.longitude,
        description=space_data.description,
        tags=space_data.tags,
        image_url=space_data.image_url,
        created_at=datetime.now(),
        is_available=True
    )
    
    parking_spaces_db[space_id] = parking_space
    return parking_space

def get_parking_spaces_near(lat: float, lng: float, radius_km: float = 5.0) -> List[ParkingSpaceResponse]:
    """Get parking spaces near a location"""
    # Simple implementation - in production, use proper geospatial queries
    nearby_spaces = []
    for space in parking_spaces_db.values():
        # Simple distance check (not accurate, just for demo)
        lat_diff = abs(space.latitude - lat)
        lng_diff = abs(space.longitude - lng)
        if lat_diff < 0.05 and lng_diff < 0.05:  # Rough 5km radius
            nearby_spaces.append(space)
    return nearby_spaces

def get_user_profile(user_id: str) -> Optional[UserProfile]:
    """Get user profile by ID"""
    return user_profiles_db.get(user_id)

def create_or_update_user_profile(user_id: str, email: str) -> UserProfile:
    """Create or update user profile"""
    existing_profile = user_profiles_db.get(user_id)
    
    if existing_profile:
        existing_profile.email = email
        return existing_profile
    else:
        profile = UserProfile(
            user_id=user_id,
            email=email,
            created_at=datetime.now()
        )
        user_profiles_db[user_id] = profile
        return profile
