import os
import sqlite3
from contextlib import contextmanager
from typing import Any

# Database configuration
DB_PATH = os.getenv("DB_PATH", "./app.db")


def init_database():
    """Initialize database with required tables"""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS parkers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                license_plate_state TEXT CHECK(length(license_plate_state) = 2),
                license_plate TEXT UNIQUE,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS places (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                added_by INTEGER NOT NULL,
                owned_by INTEGER,
                latitude DECIMAL(10, 8),
                longitude DECIMAL(10, 8),
                address TEXT NOT NULL,
                is_published BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (added_by) REFERENCES parkers (id),
                FOREIGN KEY (owned_by) REFERENCES providers (id)
            )
        """)

        # Create indexes for better performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_parkers_email ON parkers(email)")
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_parkers_username ON parkers(username)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_parkers_license_plate "
            "ON parkers(license_plate)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_providers_email ON providers(email)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_providers_username ON providers(username)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_places_latitude ON places(latitude)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_places_longitude ON places(longitude)"
        )

        conn.commit()


@contextmanager
def get_db():
    """Database connection context manager"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This makes rows behave like dicts
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# Parker CRUD operations
def create_parker(
    email: str,
    username: str,
    hashed_password: str,
    license_plate_state: str | None = None,
    license_plate: str | None = None,
) -> int:
    """Create a new parker and return the parker ID"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO parkers (email, username, hashed_password,
                license_plate_state, license_plate)
            VALUES (?, ?, ?, ?, ?)
        """,
            (email, username, hashed_password, license_plate_state, license_plate),
        )
        return cursor.lastrowid or 0


def get_parker_by_email(email: str) -> dict[str, Any] | None:
    """Get parker by email"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM parkers WHERE email = ?
        """,
            (email,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_provider_by_email(email: str) -> dict[str, Any] | None:
    """Get provider by email"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM providers WHERE email = ?
        """,
            (email,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_parker_by_id(parker_id: int) -> dict[str, Any] | None:
    """Get parker by ID"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM parkers WHERE id = ?
        """,
            (parker_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_provider_by_id(provider_id: int) -> dict[str, Any] | None:
    """Get provider by ID"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM providers WHERE id = ?
        """,
            (provider_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def create_provider(email: str, username: str, hashed_password: str) -> int:
    """Create a new provider and return the provider ID"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO providers (email, username, hashed_password)
            VALUES (?, ?, ?)
        """,
            (email, username, hashed_password),
        )
        return cursor.lastrowid or 0


# Place CRUD operations
def create_place(
    title: str,
    description: str,
    added_by: int,
    owned_by: int | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    address: str | None = None,
) -> int:
    """Create a new place and return the place ID"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO places (title, description, added_by, owned_by,
                latitude, longitude, address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (title, description, added_by, owned_by, latitude, longitude, address),
        )
        return cursor.lastrowid or 0


def get_place_by_id(place_id: int) -> dict[str, Any] | None:
    """Get place by ID"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM places WHERE id = ?
        """,
            (place_id,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_places_by_owner(
    owner_id: int, skip: int = 0, limit: int = 100
) -> list[dict[str, Any]]:
    """Get places by owner ID"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM places
            WHERE owned_by = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """,
            (owner_id, limit, skip),
        )
        return [dict(row) for row in cursor.fetchall()]


def get_published_places(skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
    """Get published places"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM places
            WHERE is_published = 1
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """,
            (limit, skip),
        )
        return [dict(row) for row in cursor.fetchall()]


def search_places_by_location(
    lat: float, lng: float, radius_km: float = 1.0
) -> list[dict[str, Any]]:
    """Search places within radius of given coordinates"""
    with get_db() as conn:
        # Simple bounding box search (for MVP - in production use PostGIS)
        # 1 degree of latitude ≈ 111 km
        lat_delta = radius_km / 111.0
        # 1 degree of longitude varies by latitude
        import math

        lng_delta = radius_km / (111.0 * math.cos(math.radians(lat)))

        cursor = conn.execute(
            """
            SELECT * FROM places
            WHERE latitude BETWEEN ? AND ?
            AND longitude BETWEEN ? AND ?
            AND is_published = 1
        """,
            (lat - lat_delta, lat + lat_delta, lng - lng_delta, lng + lng_delta),
        )
        return [dict(row) for row in cursor.fetchall()]


def update_place(place_id: int, **kwargs: Any) -> bool:
    """Update a place"""
    allowed_fields = [
        "title",
        "description",
        "latitude",
        "longitude",
        "address",
        "is_published",
    ]
    updates: list[str] = []
    params: list[Any] = []

    for field, value in kwargs.items():
        if field in allowed_fields and value is not None:
            updates.append(f"{field} = ?")
            params.append(value)

    if not updates:
        return False

    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(place_id)

    with get_db() as conn:
        cursor = conn.execute(
            f"""
            UPDATE places
            SET {", ".join(updates)}
            WHERE id = ?
        """,
            params,
        )
        return cursor.rowcount > 0


def delete_place(place_id: int) -> bool:
    """Delete a place"""
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM places WHERE id = ?", (place_id,))
        return cursor.rowcount > 0


# Utility functions
def check_database_health() -> bool:
    """Check if database is accessible"""
    try:
        with get_db() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False


def get_parker_count() -> int:
    """Get total number of parkers"""
    with get_db() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM parkers")
        return cursor.fetchone()[0]


def get_provider_count() -> int:
    """Get total number of providers"""
    with get_db() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM providers")
        return cursor.fetchone()[0]


def get_place_count() -> int:
    """Get total number of places"""
    with get_db() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM places")
        return cursor.fetchone()[0]
