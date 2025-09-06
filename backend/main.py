from contextlib import asynccontextmanager
from typing import List, Optional
from datetime import datetime, timedelta

import anyio
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt as pyjwt
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_db = {
    "users": {},
    "spaces": {},
    "bookings": {},
}
next_id = {"user": 1, "space": 1, "booking": 1}


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


class Token(BaseModel):
    access_token: str
    token_type: str


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


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None or str(user_id) not in fake_db["users"]:
            raise HTTPException(status_code=401, detail="Invalid authentication")
        return fake_db["users"][str(user_id)]
    except pyjwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication")


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up Park Place backend...")
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
    if any(u["email"] == user.email for u in fake_db["users"].values()):
        raise HTTPException(status_code=400, detail="Email already registered")

    user_id = next_id["user"]
    next_id["user"] += 1

    user_data = {
        "id": user_id,
        "email": user.email,
        "password_hash": get_password_hash(user.password),
        "name": user.name,
        "user_type": user.user_type,
        "car_license_plate": user.car_license_plate,
        "rating": 0.0,
        "created_at": datetime.utcnow(),
    }

    fake_db["users"][str(user_id)] = user_data

    return UserResponse(
        id=user_id,
        email=user.email,
        name=user.name,
        user_type=user.user_type,
        rating=0.0,
    )


@app.post("/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = None
    for u in fake_db["users"].values():
        if u["email"] == form_data.username:
            user = u
            break

    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user["id"]})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        user_type=current_user["user_type"],
        rating=current_user["rating"],
    )


@app.get("/spaces", response_model=List[ParkingSpaceResponse])
async def get_spaces(limit: int = 100):
    spaces = list(fake_db["spaces"].values())[:limit]
    return [ParkingSpaceResponse(**space) for space in spaces]


@app.post("/spaces/search", response_model=List[ParkingSpaceResponse])
async def search_spaces(query: SearchQuery):
    # Simple distance filter (in production, use PostGIS)
    def calculate_distance(lat1, lng1, lat2, lng2):
        # Simplified distance calculation
        import math

        return (
            math.sqrt((lat1 - lat2) ** 2 + (lng1 - lng2) ** 2) * 111
        )  # rough km conversion

    results = []
    for space in fake_db["spaces"].values():
        distance = calculate_distance(query.lat, query.lng, space["lat"], space["lng"])
        if distance <= query.radius:
            if query.min_price and space["price_per_hour"] < query.min_price:
                continue
            if query.max_price and space["price_per_hour"] > query.max_price:
                continue
            results.append(ParkingSpaceResponse(**space))

    return results


@app.get("/spaces/nearby")
async def get_nearby_spaces(lat: float, lng: float, radius: float = 1.0):
    query = SearchQuery(lat=lat, lng=lng, radius=radius)
    return await search_spaces(query)


@app.post("/spaces", response_model=ParkingSpaceResponse)
async def create_space(
    space: ParkingSpace, current_user: dict = Depends(get_current_user)
):
    if current_user["user_type"] not in ["lister", "both"]:
        raise HTTPException(status_code=403, detail="Only listers can add spaces")

    space_id = next_id["space"]
    next_id["space"] += 1

    space_data = {
        "id": space_id,
        "owner_id": current_user["id"],
        **space.dict(),
        "rating": 0.0,
        "is_available": True,
        "created_at": datetime.utcnow(),
    }

    fake_db["spaces"][str(space_id)] = space_data

    return ParkingSpaceResponse(**space_data)


@app.get("/spaces/{space_id}", response_model=ParkingSpaceResponse)
async def get_space(space_id: int):
    space = fake_db["spaces"].get(str(space_id))
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    return ParkingSpaceResponse(**space)


@app.put("/spaces/{space_id}", response_model=ParkingSpaceResponse)
async def update_space(
    space_id: int, space: ParkingSpace, current_user: dict = Depends(get_current_user)
):
    existing_space = fake_db["spaces"].get(str(space_id))
    if not existing_space:
        raise HTTPException(status_code=404, detail="Space not found")

    if existing_space["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    existing_space.update(space.dict())
    return ParkingSpaceResponse(**existing_space)


@app.delete("/spaces/{space_id}")
async def delete_space(space_id: int, current_user: dict = Depends(get_current_user)):
    space = fake_db["spaces"].get(str(space_id))
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")

    if space["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    del fake_db["spaces"][str(space_id)]
    return {"message": "Space deleted"}


@app.post("/spaces/{space_id}/upload-image")
async def upload_image(space_id: int, current_user: dict = Depends(get_current_user)):
    space = fake_db["spaces"].get(str(space_id))
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")

    if space["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    # In production, handle actual file upload to S3/storage
    space["image_url"] = f"https://placeholder.com/parking/{space_id}.jpg"
    return {"image_url": space["image_url"]}


@app.get("/bookings/my-bookings", response_model=List[BookingResponse])
async def get_my_bookings(current_user: dict = Depends(get_current_user)):
    user_bookings = [
        BookingResponse(**booking)
        for booking in fake_db["bookings"].values()
        if booking["renter_id"] == current_user["id"]
    ]
    return user_bookings


@app.post("/bookings", response_model=BookingResponse)
async def create_booking(
    booking: Booking, current_user: dict = Depends(get_current_user)
):
    space = fake_db["spaces"].get(str(booking.space_id))
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")

    # Check availability (simplified)
    for existing_booking in fake_db["bookings"].values():
        if existing_booking["space_id"] == booking.space_id:
            if not (
                booking.end_time <= existing_booking["start_time"]
                or booking.start_time >= existing_booking["end_time"]
            ):
                raise HTTPException(
                    status_code=400, detail="Space not available for this time"
                )

    booking_id = next_id["booking"]
    next_id["booking"] += 1

    hours = (booking.end_time - booking.start_time).total_seconds() / 3600
    total_price = hours * space["price_per_hour"]

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

    fake_db["bookings"][str(booking_id)] = booking_data

    return BookingResponse(**booking_data)


@app.put("/bookings/{booking_id}/cancel")
async def cancel_booking(
    booking_id: int, current_user: dict = Depends(get_current_user)
):
    booking = fake_db["bookings"].get(str(booking_id))
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking["renter_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    booking["status"] = "cancelled"
    return {"message": "Booking cancelled"}


@app.get("/bookings/space/{space_id}", response_model=List[BookingResponse])
async def get_space_bookings(
    space_id: int, current_user: dict = Depends(get_current_user)
):
    space = fake_db["spaces"].get(str(space_id))
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")

    if space["owner_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    space_bookings = [
        BookingResponse(**booking)
        for booking in fake_db["bookings"].values()
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
