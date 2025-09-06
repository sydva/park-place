from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import datetime

import anyio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend import database as db


# Temporary bookings storage until we add bookings table
bookings_db = {}
next_booking_id = 1

# Temporary current user for development
DEV_USER = {
    "id": 1,
    "email": "test@example.com",
    "username": "testuser",
    "user_type": "both",
}


class UserRegister(BaseModel):
    email: str
    password: str
    name: str
    user_type: str = "renter"  # renter, lister, both
    car_license_plate: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    user_type: str
    rating: float = 0.0


class ParkingSpace(BaseModel):
    title: str
    description: str
    lat: float
    lng: float
    price_per_hour: float
    tags: List[str] = []
    image_url: Optional[str] = None


class ParkingSpaceResponse(BaseModel):
    id: int
    owner_id: int
    title: str
    description: str
    lat: float
    lng: float
    price_per_hour: float
    tags: List[str]
    rating: float = 0.0
    is_available: bool = True
    image_url: Optional[str] = None
    created_at: datetime


class Booking(BaseModel):
    space_id: int
    start_time: datetime
    end_time: datetime


class BookingResponse(BaseModel):
    id: int
    space_id: int
    renter_id: int
    start_time: datetime
    end_time: datetime
    total_price: float
    status: str = "confirmed"
    created_at: datetime


class SearchQuery(BaseModel):
    lat: float
    lng: float
    radius: float = 1.0  # km
    min_price: Optional[float] = None
    max_price: Optional[float] = None


def get_current_user():
    """Temporary function to return dev user"""
    return DEV_USER


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up Park Place backend...")
    db.init_database()
    print("Database initialized")
    yield
    print("Shutting down...")


app = FastAPI(title="Park Place API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Park Place API", "version": "0.1.0"}


@app.post("/auth/register", response_model=UserResponse)
async def register(user: UserRegister):
    # Simplified registration for now
    if user.user_type in ["renter", "both"]:
        user_id = db.create_parker(
            email=user.email,
            username=user.name,
            hashed_password="temp_hash",
            license_plate=user.car_license_plate if user.car_license_plate else None,
        )
    else:
        user_id = db.create_provider(
            email=user.email, username=user.name, hashed_password="temp_hash"
        )

    return UserResponse(
        id=user_id,
        email=user.email,
        name=user.name,
        user_type=user.user_type,
        rating=0.0,
    )


@app.post("/auth/login")
async def login():
    # Simplified login for now
    return {"message": "Login temporarily disabled"}


@app.get("/auth/me", response_model=UserResponse)
async def get_me():
    current_user = get_current_user()
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user.get("username", "testuser"),
        user_type=current_user["user_type"],
        rating=0.0,
    )


@app.get("/spaces", response_model=List[ParkingSpaceResponse])
async def get_spaces(limit: int = 100):
    places = db.get_published_places(limit=limit)
    return [
        ParkingSpaceResponse(
            id=place["id"],
            owner_id=place["owned_by"] or place["added_by"],
            title=place["title"],
            description=place["description"],
            lat=place["latitude"] or 0.0,
            lng=place["longitude"] or 0.0,
            price_per_hour=10.0,  # TODO: Add price field to database
            tags=[],  # TODO: Add tags system
            rating=0.0,
            is_available=True,
            image_url=None,
            created_at=datetime.fromisoformat(place["created_at"]),
        )
        for place in places
    ]


@app.post("/spaces/search", response_model=List[ParkingSpaceResponse])
async def search_spaces(query: SearchQuery):
    places = db.search_places_by_location(query.lat, query.lng, query.radius)

    results = []
    for place in places:
        price = 10.0  # TODO: Add price field to database

        if query.min_price and price < query.min_price:
            continue
        if query.max_price and price > query.max_price:
            continue

        results.append(
            ParkingSpaceResponse(
                id=place["id"],
                owner_id=place["owned_by"] or place["added_by"],
                title=place["title"],
                description=place["description"],
                lat=place["latitude"] or 0.0,
                lng=place["longitude"] or 0.0,
                price_per_hour=price,
                tags=[],
                rating=0.0,
                is_available=True,
                image_url=None,
                created_at=datetime.fromisoformat(place["created_at"]),
            )
        )

    return results


@app.get("/spaces/nearby")
async def get_nearby_spaces(lat: float, lng: float, radius: float = 1.0):
    query = SearchQuery(lat=lat, lng=lng, radius=radius)
    return await search_spaces(query)


@app.post("/spaces", response_model=ParkingSpaceResponse)
async def create_space(space: ParkingSpace):
    current_user = get_current_user()

    place_id = db.create_place(
        title=space.title,
        description=space.description,
        added_by=current_user["id"],
        owned_by=current_user["id"]
        if current_user["user_type"] == "provider"
        else None,
        latitude=space.lat,
        longitude=space.lng,
        address="",  # TODO: Add geocoding
    )

    place = db.get_place_by_id(place_id)
    if not place:
        raise HTTPException(status_code=500, detail="Failed to create space")

    return ParkingSpaceResponse(
        id=place_id,
        owner_id=current_user["id"],
        title=space.title,
        description=space.description,
        lat=space.lat,
        lng=space.lng,
        price_per_hour=space.price_per_hour,
        tags=space.tags,
        rating=0.0,
        is_available=True,
        image_url=space.image_url,
        created_at=datetime.fromisoformat(place["created_at"]),
    )


@app.get("/spaces/{space_id}", response_model=ParkingSpaceResponse)
async def get_space(space_id: int):
    place = db.get_place_by_id(space_id)
    if not place:
        raise HTTPException(status_code=404, detail="Space not found")

    return ParkingSpaceResponse(
        id=place["id"],
        owner_id=place["owned_by"] or place["added_by"],
        title=place["title"],
        description=place["description"],
        lat=place["latitude"] or 0.0,
        lng=place["longitude"] or 0.0,
        price_per_hour=10.0,  # TODO: Add price field
        tags=[],
        rating=0.0,
        is_available=True,
        image_url=None,
        created_at=datetime.fromisoformat(place["created_at"]),
    )


@app.put("/spaces/{space_id}", response_model=ParkingSpaceResponse)
async def update_space(space_id: int, space: ParkingSpace):
    current_user = get_current_user()
    place = db.get_place_by_id(space_id)
    if not place:
        raise HTTPException(status_code=404, detail="Space not found")

    if (
        place["owned_by"] != current_user["id"]
        and place["added_by"] != current_user["id"]
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    db.update_place(
        space_id,
        title=space.title,
        description=space.description,
        latitude=space.lat,
        longitude=space.lng,
    )

    updated_place = db.get_place_by_id(space_id)
    if not updated_place:
        raise HTTPException(status_code=404, detail="Space not found after update")

    return ParkingSpaceResponse(
        id=updated_place["id"],
        owner_id=updated_place["owned_by"] or updated_place["added_by"],
        title=updated_place["title"],
        description=updated_place["description"],
        lat=updated_place["latitude"] or 0.0,
        lng=updated_place["longitude"] or 0.0,
        price_per_hour=space.price_per_hour,
        tags=space.tags,
        rating=0.0,
        is_available=True,
        image_url=space.image_url,
        created_at=datetime.fromisoformat(updated_place["created_at"]),
    )


@app.delete("/spaces/{space_id}")
async def delete_space(space_id: int):
    current_user = get_current_user()
    place = db.get_place_by_id(space_id)
    if not place:
        raise HTTPException(status_code=404, detail="Space not found")

    if (
        place["owned_by"] != current_user["id"]
        and place["added_by"] != current_user["id"]
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    db.delete_place(space_id)
    return {"message": "Space deleted"}


@app.post("/spaces/{space_id}/upload-image")
async def upload_image(space_id: int):
    current_user = get_current_user()
    place = db.get_place_by_id(space_id)
    if not place:
        raise HTTPException(status_code=404, detail="Space not found")

    if (
        place["owned_by"] != current_user["id"]
        and place["added_by"] != current_user["id"]
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    # TODO: Handle actual file upload
    image_url = f"https://placeholder.com/parking/{space_id}.jpg"
    return {"image_url": image_url}


@app.get("/bookings/my-bookings", response_model=List[BookingResponse])
async def get_my_bookings():
    current_user = get_current_user()
    user_bookings = [
        BookingResponse(**booking)
        for booking in bookings_db.values()
        if booking["renter_id"] == current_user["id"]
    ]
    return user_bookings


@app.post("/bookings", response_model=BookingResponse)
async def create_booking(booking: Booking):
    global next_booking_id
    current_user = get_current_user()

    place = db.get_place_by_id(booking.space_id)
    if not place:
        raise HTTPException(status_code=404, detail="Space not found")

    # Check availability (simplified)
    for existing_booking in bookings_db.values():
        if existing_booking["space_id"] == booking.space_id:
            if not (
                booking.end_time <= existing_booking["start_time"]
                or booking.start_time >= existing_booking["end_time"]
            ):
                raise HTTPException(
                    status_code=400, detail="Space not available for this time"
                )

    booking_id = next_booking_id
    next_booking_id += 1

    hours = (booking.end_time - booking.start_time).total_seconds() / 3600
    total_price = hours * 10.0  # TODO: Get price from database

    booking_data = {
        "id": booking_id,
        "space_id": booking.space_id,
        "renter_id": current_user["id"],
        "start_time": booking.start_time,
        "end_time": booking.end_time,
        "total_price": total_price,
        "status": "confirmed",
        "created_at": datetime.utcnow(),
    }

    bookings_db[str(booking_id)] = booking_data

    return BookingResponse(**booking_data)


@app.put("/bookings/{booking_id}/cancel")
async def cancel_booking(booking_id: int):
    current_user = get_current_user()
    booking = bookings_db.get(str(booking_id))
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking["renter_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    booking["status"] = "cancelled"
    return {"message": "Booking cancelled"}


@app.get("/bookings/space/{space_id}", response_model=List[BookingResponse])
async def get_space_bookings(space_id: int):
    current_user = get_current_user()
    place = db.get_place_by_id(space_id)
    if not place:
        raise HTTPException(status_code=404, detail="Space not found")

    if (
        place["owned_by"] != current_user["id"]
        and place["added_by"] != current_user["id"]
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    space_bookings = [
        BookingResponse(**booking)
        for booking in bookings_db.values()
        if booking["space_id"] == space_id
    ]
    return space_bookings


if __name__ == "__main__":
    import uvicorn

    async def main():
        config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, reload=True)
        server = uvicorn.Server(config)
        await server.serve()

    anyio.run(main)
