import time
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path as FilePath
from typing import Annotated, Any, TypedDict

import anyio
import database as db
from fastapi import (
    BackgroundTasks,
    FastAPI,
    File,
    Form,
    HTTPException,
    Path,
    Query,
    UploadFile,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator


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
    email: EmailStr
    name: str = Field(..., min_length=1, max_length=100)
    user_type: str = "parker"  # parker, provider, both
    car_license_plate: str | None = None
    units_preference: str | None = Field(None, pattern="^(imperial|metric)$")


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    name: str
    user_type: str
    rating: float = 0.0


class ParkingSpace(BaseModel):
    title: str | None = None
    description: str | None = None
    lat: float
    lng: float
    price_per_hour: float = Field(default=0.0, ge=0)  # Must be non-negative
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
    title: str | None = None
    description: str | None = None
    lat: float
    lng: float
    price_per_hour: float = 0.0
    tags: list[str]
    rating: float = 0.0
    is_available: bool = True
    requires_verification: bool = False
    image_url: str | None = None
    created_at: str  # ISO format string with Z suffix


class Booking(BaseModel):
    model_config = {"extra": "forbid"}

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
    radius: Annotated[float, Field(gt=0, le=1000)] = 1.0  # km, positive and reasonable max
    min_price: Annotated[float, Field(ge=0)] | None = None
    max_price: Annotated[float, Field(ge=0)] | None = None


class ReportLicensePlate(BaseModel):
    license_plate: str = Field(..., min_length=1)
    space_id: int | None = Field(None, ge=1, le=2147483647)
    description: str = Field(..., min_length=1)
    reporter_email: EmailStr | None = None


class VerificationSubmission(BaseModel):
    user_email: EmailStr


class VerificationStatus(BaseModel):
    user_email: EmailStr
    status: str  # pending, verified, rejected
    profile_photo_url: str | None = None
    id_document_url: str | None = None
    vehicle_registration_url: str | None = None
    verification_notes: str | None = None
    verified_at: str | None = None
    created_at: str


class VerificationStatusUpdate(BaseModel):
    status: str  # verified, rejected
    verification_notes: str | None = None
    verified_by: str | None = None


class CreateUserRating(BaseModel):
    ratee_id: int = Field(..., ge=1, le=2147483647)
    rating: int = Field(..., ge=1, le=5)
    description: str | None = None

    @field_validator("ratee_id", mode="before")
    @classmethod
    def convert_ratee_id(cls, v: Any) -> int:
        if isinstance(v, bool):
            raise ValueError("ratee_id must be an integer, not a boolean")
        if isinstance(v, dict):
            raise ValueError("ratee_id must be an integer, not an object")
        try:
            return int(v)
        except (TypeError, ValueError) as e:
            raise ValueError(f"ratee_id must be an integer: {e}") from e


class CreatePlaceRating(BaseModel):
    place_id: int = Field(..., ge=1, le=2147483647)
    rating: int = Field(..., ge=1, le=5)
    description: str | None = None

    @field_validator("place_id", mode="before")
    @classmethod
    def convert_place_id(cls, v: Any) -> int:
        if isinstance(v, bool):
            raise ValueError("place_id must be an integer, not a boolean")
        if isinstance(v, dict):
            raise ValueError("place_id must be an integer, not an object")
        try:
            return int(v)
        except (TypeError, ValueError) as e:
            raise ValueError(f"place_id must be an integer: {e}") from e


class RatingResponse(BaseModel):
    id: int
    rating: int
    description: str | None
    created_at: str


def get_current_user() -> dict[str, Any]:
    """Temporary function to return dev user"""
    return DEV_USER


async def send_rating_reminder(email: str, place_id: int):
    try:
        db.create_notification(
            user_email=email,
            title="Rate your recent parking",
            message=f"Your parking session just ended. Please rate place #{place_id}.",
            notification_type="info",
        )
    except Exception as e:
        print(f"Failed to send rating reminder: {e}")


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

    existing_user = db.get_user_by_email(user.email)
    if existing_user:
        # For testing, make it unique
        unique_suffix = str(int(time.time() * 1000000))[-8:]
        # Keep email valid by adding suffix before @ sign
        email_parts = user.email.split("@")
        if len(email_parts) == 2:
            user.email = f"{email_parts[0]}{unique_suffix}@{email_parts[1]}"
        else:
            user.email = f"{user.email}{unique_suffix}@example.com"
        user.name = f"{user.name}_{unique_suffix}"

    # Create user
    try:
        user_id = db.create_user(
            email=user.email,
            username=user.name,
            hashed_password="temp_hash",
            license_plate_state=license_plate_state,
            license_plate=license_plate_number,
        )
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            # Try again with unique username
            unique_suffix = str(int(time.time() * 1000000))[-8:]
            user.name = f"{user.name}_{unique_suffix}"
            user.email = f"{user.email}_{unique_suffix}"
            user_id = db.create_user(
                email=user.email,
                username=user.name,
                hashed_password="temp_hash",
                license_plate_state=license_plate_state,
                license_plate=license_plate_number,
            )
        else:
            raise HTTPException(status_code=500, detail="Registration failed") from None

    # User type "both" is now handled in the single unified users table
    # No need for separate provider record creation

    return UserResponse(
        id=user_id,
        email=user.email,
        name=user.name,
        user_type="parker",  # Default for all users now
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


@app.get("/users/profile", responses={404: {"description": "User not found"}})
async def get_user_profile(email: str):
    """Get user profile by email from database"""
    user = db.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=404, detail="User profile not found")

    return {
        "id": user["id"],
        "email": user["email"],
        "username": user["username"],
        "user_type": user["user_type"],
        "license_plate": user.get("license_plate"),
        "license_plate_state": user.get("license_plate_state"),
        "units_preference": user.get("units_preference"),
        "is_active": user["is_active"],
        "is_verified": user.get("is_verified", False),
        "created_at": user["created_at"],
    }


@app.put("/users/update-profile", responses={404: {"description": "User not found"}})
async def update_user_profile(user_data: UserRegister):
    """Update user profile by email"""
    try:
        # Check if user exists
        user = db.get_user_by_email(user_data.email)
        if not user:
            raise HTTPException(status_code=404, detail="User profile not found")

        # Parse license plate if provided
        license_plate_state = None
        license_plate_number = None
        if user_data.car_license_plate and len(user_data.car_license_plate) >= 2:
            license_plate_state = user_data.car_license_plate[:2].upper()
            license_plate_number = user_data.car_license_plate[2:].upper()

        # Update the user record
        success = db.update_user(
            email=user_data.email,
            username=user_data.name,
            license_plate=license_plate_number,
            license_plate_state=license_plate_state,
            units_preference=user_data.units_preference,
        )

        if not success:
            raise HTTPException(status_code=500, detail="Failed to update profile")

        # Return updated profile
        updated_user = db.get_user_by_email(user_data.email)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found after update")
        return {
            "id": updated_user["id"],
            "email": updated_user["email"],
            "username": updated_user["username"],
            "user_type": updated_user["user_type"],
            "license_plate": updated_user.get("license_plate"),
            "license_plate_state": updated_user.get("license_plate_state"),
            "units_preference": updated_user.get("units_preference"),
            "is_active": updated_user["is_active"],
            "created_at": updated_user["created_at"],
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to update profile") from e


@app.get("/spaces", response_model=list[ParkingSpaceResponse])
async def get_spaces(limit: Annotated[int, Query(ge=1, le=10000)] = 100):
    places = db.get_published_places(limit=limit)
    return [
        ParkingSpaceResponse(
            id=place["id"],
            owner_id=place["added_by"],
            title=place["title"],
            description=place["description"],
            lat=place["latitude"] or 0.0,
            lng=place["longitude"] or 0.0,
            price_per_hour=place.get("price_per_hour", 0.0),
            tags=[],  # TODO: Add tags system
            rating=0.0,
            is_available=True,
            requires_verification=place.get("requires_verification", False),
            image_url=None,
            created_at=place["created_at"] + "Z" if not place["created_at"].endswith("Z") else place["created_at"],
        )
        for place in places
    ]


@app.post("/spaces/search", response_model=list[ParkingSpaceResponse])
async def search_spaces(query: SearchQuery):
    places = db.search_places_by_location(query.lat, query.lng, query.radius)

    results: list[ParkingSpaceResponse] = []
    for place in places:
        price = place.get("price_per_hour", 0.0)

        if query.min_price and price < query.min_price:
            continue
        if query.max_price and price > query.max_price:
            continue

        # Parse tags from JSON string
        import json

        tags = []
        if place.get("tags"):
            try:
                tags = json.loads(place["tags"]) if isinstance(place["tags"], str) else place["tags"]
            except (json.JSONDecodeError, TypeError):
                tags = []

        results.append(
            ParkingSpaceResponse(
                id=place["id"],
                owner_id=place["added_by"],
                title=place["title"],
                description=place["description"],
                lat=place["latitude"] or 0.0,
                lng=place["longitude"] or 0.0,
                price_per_hour=price,
                tags=tags,
                rating=0.0,
                is_available=True,
                requires_verification=place.get("verified_only", False),
                image_url=None,
                created_at=place["created_at"] + "Z" if not place["created_at"].endswith("Z") else place["created_at"],
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
        added_by=current_user["id"],
        title=space.title,
        description=space.description,
        creator_is_owner=current_user["user_type"] == "provider",
        latitude=space.lat,
        longitude=space.lng,
        address="",  # TODO: Add geocoding
        price_per_hour=space.price_per_hour,
        tags=space.tags,
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
        requires_verification=False,  # New spaces don't require verification by default
        image_url=space.image_url,
        created_at=place["created_at"] + "Z" if not place["created_at"].endswith("Z") else place["created_at"],
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
        owner_id=place["added_by"],
        title=place["title"],
        description=place["description"],
        lat=place["latitude"] or 0.0,
        lng=place["longitude"] or 0.0,
        price_per_hour=place.get("price_per_hour", 0.0),
        tags=[],
        rating=0.0,
        is_available=True,
        requires_verification=place.get("requires_verification", False),
        image_url=None,
        created_at=place["created_at"] + "Z" if not place["created_at"].endswith("Z") else place["created_at"],
    )


@app.put(
    "/spaces/{space_id}",
    response_model=ParkingSpaceResponse,
    responses={
        404: {"description": "Space not found"},
        403: {"description": "Not authorized"},
    },
)
async def update_space(space_id: Annotated[int, Path(ge=0, le=2147483647)], space: ParkingSpace):
    current_user = get_current_user()
    place = db.get_place_by_id(space_id)
    if not place:
        raise HTTPException(status_code=404, detail="Space not found")

    if place["added_by"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    db.update_place(
        space_id,
        title=space.title,
        description=space.description,
        latitude=space.lat,
        longitude=space.lng,
        price_per_hour=space.price_per_hour,
    )

    updated_place = db.get_place_by_id(space_id)
    if not updated_place:
        raise HTTPException(status_code=404, detail="Space not found after update")

    return ParkingSpaceResponse(
        id=updated_place["id"],
        owner_id=updated_place["added_by"],
        title=updated_place["title"],
        description=updated_place["description"],
        lat=updated_place["latitude"] or 0.0,
        lng=updated_place["longitude"] or 0.0,
        price_per_hour=space.price_per_hour,
        tags=space.tags,
        rating=0.0,
        is_available=True,
        requires_verification=updated_place.get("requires_verification", False),
        image_url=space.image_url,
        created_at=updated_place["created_at"] + "Z" if not updated_place["created_at"].endswith("Z") else updated_place["created_at"],
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

    if place["added_by"] != current_user["id"]:
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
async def upload_image(space_id: Annotated[int, Path(ge=0, le=2147483647)], file: UploadFile = File(...)):
    current_user = get_current_user()
    place = db.get_place_by_id(space_id)
    if not place:
        raise HTTPException(status_code=404, detail="Space not found")

    if place["added_by"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Generate unique filename
    file_extension = file.filename.split(".")[-1] if file.filename and "." in file.filename else "jpg"
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
async def create_booking(booking: Booking, background_tasks: BackgroundTasks):
    global next_booking_id
    current_user = get_current_user()

    place = db.get_place_by_id(booking.space_id)
    if not place:
        raise HTTPException(status_code=404, detail="Space not found")

    # Check availability (simplified)
    for existing_booking in bookings_db.values():
        if existing_booking["space_id"] == booking.space_id and not (booking.end_time <= existing_booking["start_time"] or booking.start_time >= existing_booking["end_time"]):
            raise HTTPException(status_code=400, detail="Space not available for this time")

    booking_id = next_booking_id
    next_booking_id += 1

    hours = (booking.end_time - booking.start_time).total_seconds() / 3600
    total_price = hours * place.get("price_per_hour", 0.0)

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

    # Schedule a rating reminder shortly after end_time (MVP: send immediately if in past)
    max(0, int((booking.end_time - datetime.utcnow()).total_seconds()))
    # Using background task without actual delay for simplicity; in production use a scheduler
    background_tasks.add_task(send_rating_reminder, current_user["email"], booking.space_id)

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

    if place["added_by"] != current_user["id"]:
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
    try:
        # Create the license plate report
        report_id = db.create_license_plate_report(
            license_plate=report.license_plate,
            description=report.description,
            reporter_email=report.reporter_email,
            space_id=report.space_id,
        )

        # Find the owner of the reported license plate and send notification
        # Find user by license plate
        parker = db.get_user_by_license_plate(report.license_plate)
        if parker:
            # Create notification for the owner of the license plate
            db.create_notification(
                user_email=parker["email"],
                title="License Plate Reported",
                message=f"Your license plate {report.license_plate} has been reported. Reason: {report.description}",
                notification_type="warning",
            )

        return {
            "message": "License plate report submitted successfully",
            "report_id": report_id,
        }
    except Exception as e:
        print(f"Error creating license plate report: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit report") from e


@app.get("/reports", responses={501: {"description": "Not implemented"}})
async def get_reports():
    try:
        reports = db.get_license_plate_reports()
        return reports
    except Exception as e:
        print(f"Error getting reports: {e}")
        raise HTTPException(status_code=500, detail="Failed to get reports") from e


@app.post("/verification/upload", response_model=dict, responses={400: {"description": "Bad request"}})
async def upload_verification_documents(
    profile_photo: UploadFile = File(...),
    id_document: UploadFile = File(...),
    vehicle_registration: UploadFile = File(...),
    user_email: EmailStr = Form(...),
):
    """Upload verification documents for identity verification"""
    try:
        # Validate that files are actually uploaded
        for file, name in [
            (profile_photo, "profile photo"),
            (id_document, "ID document"),
            (vehicle_registration, "vehicle registration"),
        ]:
            if not file or not hasattr(file, "content_type") or not file.filename:
                raise HTTPException(
                    status_code=422,
                    detail=f"Invalid or missing {name}. File upload required.",
                )

        # Validate file types (basic validation)
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "application/pdf"]

        for file, name in [
            (profile_photo, "profile photo"),
            (id_document, "ID document"),
            (vehicle_registration, "vehicle registration"),
        ]:
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid file type for {name}. Only JPEG, PNG, and PDF allowed.",
                )

        # Create unique filenames with timestamp
        import uuid

        timestamp = int(time.time())

        def create_filename(original_name: str, doc_type: str) -> str:
            ext = original_name.split(".")[-1] if "." in original_name else "jpg"
            return f"{doc_type}_{user_email.replace('@', '_')}_{timestamp}_{uuid.uuid4().hex[:8]}.{ext}"

        # Save files
        profile_photo_filename = create_filename(profile_photo.filename or "photo.jpg", "profile")
        id_document_filename = create_filename(id_document.filename or "id.jpg", "id")
        vehicle_reg_filename = create_filename(vehicle_registration.filename or "registration.jpg", "vehicle")

        # Save files to upload directory
        for file, filename in [
            (profile_photo, profile_photo_filename),
            (id_document, id_document_filename),
            (vehicle_registration, vehicle_reg_filename),
        ]:
            file_path = UPLOAD_DIR / filename
            contents = await file.read()
            with open(file_path, "wb") as f:
                f.write(contents)

        # Create verification record in database
        verification_id = db.create_user_verification(
            user_email=user_email,
            profile_photo_url=f"/uploads/{profile_photo_filename}",
            id_document_url=f"/uploads/{id_document_filename}",
            vehicle_registration_url=f"/uploads/{vehicle_reg_filename}",
        )

        # Send notification to user
        db.create_notification(
            user_email=user_email,
            title="Verification Documents Submitted",
            message="Your verification documents have been submitted for review. You will be notified once the review is complete.",
            notification_type="info",
        )

        return {
            "message": "Verification documents uploaded successfully",
            "verification_id": verification_id,
            "status": "pending",
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error uploading verification documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload verification documents") from e


@app.get("/verification/status", response_model=VerificationStatus)
async def get_verification_status(email: EmailStr):
    """Get user's verification status"""
    try:
        verification = db.get_user_verification(email)
        if not verification:
            # Return default status for users who haven't started verification
            return VerificationStatus(
                user_email=email,
                status="not_started",
                created_at=datetime.now().isoformat(),
            )

        return VerificationStatus(
            user_email=verification["user_email"],
            status=verification["status"],
            profile_photo_url=verification.get("profile_photo_url"),
            id_document_url=verification.get("id_document_url"),
            vehicle_registration_url=verification.get("vehicle_registration_url"),
            verification_notes=verification.get("verification_notes"),
            verified_at=verification.get("verified_at"),
            created_at=verification["created_at"],
        )
    except Exception as e:
        print(f"Error getting verification status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get verification status") from e


@app.put("/verification/admin/update-status", responses={404: {"description": "Verification record not found"}})
async def update_verification_status_admin(user_email: EmailStr, update: VerificationStatusUpdate):
    """Update verification status (admin only - simplified for MVP)"""
    try:
        success = db.update_verification_status(
            user_email=user_email,
            status=update.status,
            verified_by=update.verified_by or "admin",
            verification_notes=update.verification_notes,
        )

        if not success:
            raise HTTPException(status_code=404, detail="Verification record not found")

        # Send notification to user
        if update.status == "verified":
            notification_title = "Verification Approved"
            notification_message = "Congratulations! Your identity has been verified. You now have access to verified-only parking spaces."
        else:
            notification_title = "Verification Rejected"
            notification_message = f"Your verification was not approved. Reason: {update.verification_notes or 'Please resubmit with clearer documents.'}"

        db.create_notification(
            user_email=user_email,
            title=notification_title,
            message=notification_message,
            notification_type="info" if update.status == "verified" else "warning",
        )

        return {"message": f"Verification status updated to {update.status}"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating verification status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update verification status") from e


@app.get("/verification/admin/pending")
async def get_pending_verifications_admin():
    """Get all pending verifications (admin only)"""
    try:
        pending = db.get_pending_verifications()
        return pending
    except Exception as e:
        print(f"Error getting pending verifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to get pending verifications") from e


@app.get("/notifications")
async def get_user_notifications(email: str):
    """Get notifications for a user"""
    try:
        notifications = db.get_user_notifications(email)
        return notifications
    except Exception as e:
        print(f"Error getting notifications: {e}")
        raise HTTPException(status_code=500, detail="Failed to get notifications") from e


@app.get("/notifications/unread-count")
async def get_unread_count(email: str):
    """Get count of unread notifications for a user"""
    try:
        count = db.get_unread_notification_count(email)
        return {"unread_count": count}
    except Exception as e:
        print(f"Error getting unread count: {e}")
        raise HTTPException(status_code=500, detail="Failed to get unread count") from e


@app.put("/notifications/{notification_id}/read", responses={404: {"description": "Notification not found"}})
async def mark_notification_read(notification_id: int):
    """Mark a notification as read"""
    try:
        success = db.mark_notification_read(notification_id)
        if not success:
            raise HTTPException(status_code=404, detail="Notification not found")
        return {"message": "Notification marked as read"}
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error marking notification as read: {e}")
        raise HTTPException(status_code=500, detail="Failed to mark notification as read") from e


# Rating endpoints
@app.post("/ratings/users", response_model=dict)
async def create_user_rating(rating: CreateUserRating):
    """Create a rating for a user"""
    try:
        current_user = get_current_user()
        rating_id = db.create_user_rating(
            rater_id=current_user["id"],
            ratee_id=rating.ratee_id,
            rating=rating.rating,
            description=rating.description,
        )
        return {"id": rating_id, "message": "User rating created successfully"}
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=409, detail="You have already rated this user") from e
        print(f"Error creating user rating: {e}")
        raise HTTPException(status_code=500, detail="Failed to create user rating") from e


@app.post("/ratings/places", response_model=dict)
async def create_place_rating(rating: CreatePlaceRating):
    """Create a rating for a place"""
    try:
        current_user = get_current_user()
        rating_id = db.create_place_rating(
            user_id=current_user["id"],
            place_id=rating.place_id,
            rating=rating.rating,
            description=rating.description,
        )
        return {"id": rating_id, "message": "Place rating created successfully"}
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=409, detail="You have already rated this place") from e
        print(f"Error creating place rating: {e}")
        raise HTTPException(status_code=500, detail="Failed to create place rating") from e


@app.get("/ratings/places/{place_id}")
async def get_place_ratings(place_id: int = Path(..., ge=1, le=2147483647)):
    """Get all ratings for a specific place"""
    try:
        ratings = db.get_place_ratings(place_id)
        return {
            "ratings": ratings,
            "count": len(ratings),
            "average": db.get_place_average_rating(place_id),
        }
    except Exception as e:
        print(f"Error getting place ratings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get place ratings") from e


@app.get("/ratings/users/{user_id}")
async def get_user_ratings(user_id: int = Path(..., ge=1, le=2147483647)):
    """Get all ratings for a specific user"""
    try:
        ratings = db.get_user_ratings_by_ratee(user_id)
        return {
            "ratings": ratings,
            "count": len(ratings),
            "average": db.get_user_average_rating(user_id),
        }
    except Exception as e:
        print(f"Error getting user ratings: {e}")
        raise HTTPException(status_code=500, detail="Failed to get user ratings") from e


if __name__ == "__main__":
    import uvicorn

    async def main():
        config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, reload=True)
        server = uvicorn.Server(config)
        await server.serve()

    anyio.run(main)
