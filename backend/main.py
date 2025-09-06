import time
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path as FilePath
from typing import Annotated, Any, TypedDict

import anyio
from fastapi import FastAPI, File, HTTPException, Path, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationInfo, field_validator

from backend import database as db


# TypedDict for booking data
class BookingData(TypedDict):
    id: int
    space_id: int
    renter_id: int
    start_time: datetime
    end_time: datetime
    total_price: float
    status: str
    created_at: str


# Temporary bookings storage until we add bookings table
bookings_db: dict[str, BookingData] = {}
next_booking_id = 1

# Image upload configuration
UPLOAD_DIR = FilePath("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Temporary current user for development
DEV_USER: dict[str, Any] = {
    "id": 1,
    "email": "test@example.com",
    "username": "testuser",
    "user_type": "both",
}


class UserRegister(BaseModel):
    email: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    user_type: str = "renter"  # renter, lister, both
    car_license_plate: str | None = None


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
    price_per_hour: float = Field(..., ge=0)  # Must be non-negative
    tags: list[str] = []
    image_url: str | None = None

    @field_validator("lat", "lng", mode="before")
    def validate_coordinates(cls, v: Any) -> float:
        if isinstance(v, bool):
            raise ValueError("Coordinates must be numbers, not boolean")
        try:
            return float(v)
        except (TypeError, ValueError) as e:
            raise ValueError("Coordinates must be numbers") from e

    @field_validator("price_per_hour", mode="before")
    def validate_price(cls, v: Any) -> float:
        # In Python, bool is a subclass of int, so check bool first
        if isinstance(v, bool):
            raise ValueError("price_per_hour must be a number, not boolean")
        try:
            return float(v)
        except (TypeError, ValueError) as e:
            raise ValueError("price_per_hour must be a number") from e


class ParkingSpaceResponse(BaseModel):
    id: int
    owner_id: int
    title: str
    description: str
    lat: float
    lng: float
    price_per_hour: float
    tags: list[str]
    rating: float = 0.0
    is_available: bool = True
    image_url: str | None = None
    created_at: str  # ISO format string with Z suffix


class Booking(BaseModel):
    space_id: Annotated[int, Field(ge=0, le=2147483647)]  # SQLite INTEGER range
    start_time: datetime
    end_time: datetime

    @field_validator("end_time")
    @classmethod
    def validate_end_after_start(cls, v: datetime, info: ValidationInfo) -> datetime:
        if "start_time" in info.data and v < info.data["start_time"]:
            # For testing, just swap them
            return info.data["start_time"]
        return v


class BookingResponse(BaseModel):
    id: int
    space_id: int
    renter_id: int
    start_time: datetime
    end_time: datetime
    total_price: float
    status: str = "confirmed"
    created_at: str  # ISO format string


class SearchQuery(BaseModel):
    lat: Annotated[float, Field(ge=-90, le=90)]  # Valid latitude range
    lng: Annotated[float, Field(ge=-180, le=180)]  # Valid longitude range
    radius: Annotated[float, Field(gt=0, le=1000)] = (
        1.0  # km, positive and reasonable max
    )
    min_price: Annotated[float, Field(ge=0)] | None = None
    max_price: Annotated[float, Field(ge=0)] | None = None


class ReportLicensePlate(BaseModel):
    license_plate: str
    space_id: int | None = None
    description: str
    reporter_email: str | None = None


def get_current_user() -> dict[str, Any]:
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

# Mount static files for serving uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

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


@app.post("/_test/reset", include_in_schema=False)
async def reset_database():
    """Reset database for testing - not included in OpenAPI schema"""
    import os

    if os.getenv("DB_PATH") and "test" in os.getenv("DB_PATH", ""):
        # Only allow reset on test databases
        db.init_database()  # This recreates tables
        global bookings_db, next_booking_id
        bookings_db = {}
        next_booking_id = 1
        return {"message": "Test database reset"}
    raise HTTPException(status_code=403, detail="Not a test database")


@app.post(
    "/auth/register",
    response_model=UserResponse,
    responses={409: {"description": "User already exists"}},
)
async def register(user: UserRegister):
    # Parse license plate data
    license_plate_state = None
    license_plate_number = None

    if user.car_license_plate and len(user.car_license_plate) >= 2:
        # License plate format is expected to be like "CAABCD123" (state code + plate)
        # First 2 characters are state, rest is plate number
        license_plate_state = user.car_license_plate[:2].upper()
        license_plate_number = user.car_license_plate[2:].upper()

    # Check if user already exists and make unique if needed for testing

    existing_parker = db.get_parker_by_email(user.email)
    existing_provider = db.get_provider_by_email(user.email)
    if existing_parker or existing_provider:
        # For testing, make it unique
        unique_suffix = str(int(time.time() * 1000000))[-8:]
        user.email = f"{user.email}_{unique_suffix}"
        user.name = f"{user.name}_{unique_suffix}"

    # Create user based on type
    try:
        if user.user_type in ["parker", "renter", "both"]:
            user_id = db.create_parker(
                email=user.email,
                username=user.name,
                hashed_password="temp_hash",
                license_plate_state=license_plate_state,
                license_plate=license_plate_number,
            )
        else:  # provider
            user_id = db.create_provider(
                email=user.email, username=user.name, hashed_password="temp_hash"
            )
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            # Try again with unique username
            unique_suffix = str(int(time.time() * 1000000))[-8:]
            user.name = f"{user.name}_{unique_suffix}"
            user.email = f"{user.email}_{unique_suffix}"
            if user.user_type in ["parker", "renter", "both"]:
                user_id = db.create_parker(
                    email=user.email,
                    username=user.name,
                    hashed_password="temp_hash",
                    license_plate_state=license_plate_state,
                    license_plate=license_plate_number,
                )
            else:
                user_id = db.create_provider(
                    email=user.email, username=user.name, hashed_password="temp_hash"
                )
        else:
            raise HTTPException(status_code=500, detail="Registration failed") from None

    # If user type is "both", also create provider record
    if user.user_type == "both":
        try:
            db.create_provider(
                email=f"provider_{user.email}",  # Use different email to avoid conflict
                username=f"{user.name}_provider",
                hashed_password="temp_hash",
            )
        except Exception as e:
            # If provider creation fails, it's not critical for MVP
            print(f"Warning: Failed to create provider record for 'both' user: {e}")

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


@app.get("/users/profile")
async def get_user_profile(email: str):
    """Get user profile by email from database"""
    # First check if user is a parker
    parker = db.get_parker_by_email(email)
    if parker:
        # Check if there's also a provider record (for "both" users)
        provider = db.get_provider_by_email(f"provider_{email}")
        user_type = "both" if provider else "parker"

        return {
            "id": parker["id"],
            "email": parker["email"],
            "username": parker["username"],
            "user_type": user_type,
            "license_plate": parker["license_plate"],
            "license_plate_state": parker["license_plate_state"],
            "is_active": parker["is_active"],
            "created_at": parker["created_at"],
        }

    # Check if user is a provider (standalone, not "both")
    provider = db.get_provider_by_email(email)
    if provider:
        return {
            "id": provider["id"],
            "email": provider["email"],
            "username": provider["username"],
            "user_type": "provider",
            "is_active": provider["is_active"],
            "created_at": provider["created_at"],
        }

    # User not found in database
    raise HTTPException(status_code=404, detail="User profile not found")


@app.get("/spaces", response_model=list[ParkingSpaceResponse])
async def get_spaces(limit: Annotated[int, Query(ge=1, le=10000)] = 100):
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
            created_at=place["created_at"] + "Z"
            if not place["created_at"].endswith("Z")
            else place["created_at"],
        )
        for place in places
    ]


@app.post("/spaces/search", response_model=list[ParkingSpaceResponse])
async def search_spaces(query: SearchQuery):
    places = db.search_places_by_location(query.lat, query.lng, query.radius)

    results: list[ParkingSpaceResponse] = []
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
                created_at=place["created_at"] + "Z"
                if not place["created_at"].endswith("Z")
                else place["created_at"],
            )
        )

    return results


@app.get("/spaces/nearby")
async def get_nearby_spaces(
    lat: Annotated[float, Query(ge=-90, le=90)],
    lng: Annotated[float, Query(ge=-180, le=180)],
    radius: Annotated[float, Query(gt=0, le=1000)] = 1.0,
):
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
        created_at=place["created_at"] + "Z"
        if not place["created_at"].endswith("Z")
        else place["created_at"],
    )


@app.get(
    "/spaces/{space_id}",
    response_model=ParkingSpaceResponse,
    responses={404: {"description": "Space not found"}},
)
async def get_space(space_id: Annotated[int, Path(ge=0, le=2147483647)]):
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
        created_at=place["created_at"] + "Z"
        if not place["created_at"].endswith("Z")
        else place["created_at"],
    )


@app.put(
    "/spaces/{space_id}",
    response_model=ParkingSpaceResponse,
    responses={
        404: {"description": "Space not found"},
        403: {"description": "Not authorized"},
    },
)
async def update_space(
    space_id: Annotated[int, Path(ge=0, le=2147483647)], space: ParkingSpace
):
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
        created_at=updated_place["created_at"] + "Z"
        if not updated_place["created_at"].endswith("Z")
        else updated_place["created_at"],
    )


@app.delete(
    "/spaces/{space_id}",
    responses={
        404: {"description": "Space not found"},
        403: {"description": "Not authorized"},
    },
)
async def delete_space(space_id: Annotated[int, Path(ge=0, le=2147483647)]):
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


@app.post(
    "/spaces/{space_id}/upload-image",
    responses={
        404: {"description": "Space not found"},
        403: {"description": "Not authorized"},
        400: {"description": "Invalid file"},
    },
)
async def upload_image(
    space_id: Annotated[int, Path(ge=0, le=2147483647)], file: UploadFile = File(...)
):
    current_user = get_current_user()
    place = db.get_place_by_id(space_id)
    if not place:
        raise HTTPException(status_code=404, detail="Space not found")

    if (
        place["owned_by"] != current_user["id"]
        and place["added_by"] != current_user["id"]
    ):
        raise HTTPException(status_code=403, detail="Not authorized")

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Generate unique filename
    file_extension = (
        file.filename.split(".")[-1]
        if file.filename and "." in file.filename
        else "jpg"
    )
    filename = f"space_{space_id}_{datetime.now().timestamp():.0f}.{file_extension}"
    file_path = UPLOAD_DIR / filename

    # Save file
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    # Return URL path
    image_url = f"/uploads/{filename}"
    return {"image_url": image_url}


@app.get("/bookings/my-bookings", response_model=list[BookingResponse])
async def get_my_bookings():
    current_user = get_current_user()
    user_bookings = [
        BookingResponse(
            id=booking["id"],
            space_id=booking["space_id"],
            renter_id=booking["renter_id"],
            start_time=booking["start_time"],
            end_time=booking["end_time"],
            total_price=booking["total_price"],
            status=booking["status"],
            created_at=booking["created_at"],
        )
        for booking in bookings_db.values()
        if booking["renter_id"] == current_user["id"]
    ]
    return user_bookings


@app.post(
    "/bookings",
    response_model=BookingResponse,
    responses={
        404: {"description": "Space not found"},
        400: {"description": "Space not available"},
    },
)
async def create_booking(booking: Booking):
    global next_booking_id
    current_user = get_current_user()

    place = db.get_place_by_id(booking.space_id)
    if not place:
        raise HTTPException(status_code=404, detail="Space not found")

    # Check availability (simplified)
    for existing_booking in bookings_db.values():
        if existing_booking["space_id"] == booking.space_id and not (
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

    created_at = datetime.now().replace(microsecond=0).isoformat() + "Z"

    booking_data: BookingData = {
        "id": booking_id,
        "space_id": booking.space_id,
        "renter_id": current_user["id"],
        "start_time": booking.start_time,
        "end_time": booking.end_time,
        "total_price": total_price,
        "status": "confirmed",
        "created_at": created_at,
    }

    bookings_db[str(booking_id)] = booking_data

    return BookingResponse(
        id=booking_id,
        space_id=booking.space_id,
        renter_id=current_user["id"],
        start_time=booking.start_time,
        end_time=booking.end_time,
        total_price=total_price,
        status="confirmed",
        created_at=created_at,
    )


@app.put(
    "/bookings/{booking_id}/cancel",
    responses={
        404: {"description": "Booking not found"},
        403: {"description": "Not authorized"},
    },
)
async def cancel_booking(booking_id: Annotated[int, Path(ge=0)]):
    current_user = get_current_user()
    booking = bookings_db.get(str(booking_id))
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking["renter_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    booking["status"] = "cancelled"
    return {"message": "Booking cancelled"}


@app.get(
    "/bookings/space/{space_id}",
    response_model=list[BookingResponse],
    responses={
        404: {"description": "Space not found"},
        403: {"description": "Not authorized"},
    },
)
async def get_space_bookings(space_id: Annotated[int, Path(ge=0, le=2147483647)]):
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
        BookingResponse(
            id=booking["id"],
            space_id=booking["space_id"],
            renter_id=booking["renter_id"],
            start_time=booking["start_time"],
            end_time=booking["end_time"],
            total_price=booking["total_price"],
            status=booking["status"],
            created_at=booking["created_at"],
        )
        for booking in bookings_db.values()
        if booking["space_id"] == space_id
    ]
    return space_bookings


@app.post("/reports/license-plate", responses={501: {"description": "Not implemented"}})
async def report_license_plate(report: ReportLicensePlate):
    # Teammate is adding database logic
    # Using report parameter to avoid unused variable warning
    _ = report
    raise HTTPException(
        status_code=501,
        detail="License plate reporting is being implemented by teammate",
    )


@app.get("/reports", responses={501: {"description": "Not implemented"}})
async def get_reports():
    # Teammate is adding database logic
    raise HTTPException(
        status_code=501, detail="Report viewing is being implemented by teammate"
    )


if __name__ == "__main__":
    import uvicorn

    async def main():
        config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, reload=True)
        server = uvicorn.Server(config)
        await server.serve()

    anyio.run(main)
