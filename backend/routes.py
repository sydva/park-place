from fastapi import APIRouter, Depends, HTTPException, Query
from supertokens_python.recipe.session.framework.fastapi import verify_session
from supertokens_python.recipe.session import SessionContainer
from typing import List
from .database import (
    ParkingSpaceCreate, 
    ParkingSpaceResponse, 
    UserProfile,
    create_parking_space,
    get_parking_spaces_near,
    get_user_profile,
    create_or_update_user_profile
)

router = APIRouter(prefix="/api", tags=["Park Place API"])

@router.get("/parking-spaces")
async def get_nearby_parking_spaces(
    lat: float = Query(..., description="Latitude"),
    lng: float = Query(..., description="Longitude"),
    radius: float = Query(5.0, description="Search radius in km")
) -> List[ParkingSpaceResponse]:
    """Get parking spaces near a location (public endpoint)"""
    return get_parking_spaces_near(lat, lng, radius)

@router.post("/parking-spaces")
async def create_new_parking_space(
    space_data: ParkingSpaceCreate,
    session: SessionContainer = Depends(verify_session())
) -> ParkingSpaceResponse:
    """Create a new parking space (authenticated endpoint)"""
    user_id = session.get_user_id()
    return create_parking_space(user_id, space_data)

@router.get("/profile")
async def get_my_profile(
    session: SessionContainer = Depends(verify_session())
) -> UserProfile:
    """Get current user's profile"""
    user_id = session.get_user_id()
    profile = get_user_profile(user_id)
    
    if not profile:
        # Create a default profile if it doesn't exist
        # In a real app, you'd get email from SuperTokens user info
        email = f"{user_id}@example.com"  # Placeholder
        profile = create_or_update_user_profile(user_id, email)
    
    return profile

@router.get("/my-parking-spaces")
async def get_my_parking_spaces(
    session: SessionContainer = Depends(verify_session())
) -> List[ParkingSpaceResponse]:
    """Get parking spaces owned by current user"""
    user_id = session.get_user_id()
    from .database import parking_spaces_db
    
    user_spaces = [
        space for space in parking_spaces_db.values() 
        if space.owner_id == user_id
    ]
    return user_spaces
