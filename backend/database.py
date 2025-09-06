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
                title TEXT,
                description TEXT,
                added_by INTEGER NOT NULL,
                owned_by INTEGER,
                latitude DECIMAL(10, 8),
                longitude DECIMAL(10, 8),
                address TEXT NOT NULL,
                price_per_hour DECIMAL(10, 2) DEFAULT 0,
                is_published BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (added_by) REFERENCES parkers (id),
                FOREIGN KEY (owned_by) REFERENCES providers (id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS license_plate_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                license_plate TEXT NOT NULL,
                description TEXT NOT NULL,
                reporter_email TEXT,
                space_id INTEGER,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (space_id) REFERENCES places (id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                type TEXT DEFAULT 'info',
                is_read BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

        # Add price_per_hour column if it doesn't exist (for existing databases)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(places)")
        columns = [column[1] for column in cursor.fetchall()]
        if "price_per_hour" not in columns:
            conn.execute(
                "ALTER TABLE places ADD COLUMN price_per_hour DECIMAL(10, 2) DEFAULT 0"
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


def get_parker_by_license_plate(license_plate: str) -> dict[str, Any] | None:
    """Get parker by license plate"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM parkers WHERE license_plate = ?
        """,
            (license_plate,),
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


def update_parker_profile(email: str, username: str, license_plate: str | None = None) -> bool:
    """Update parker profile fields"""
    try:
        with get_db() as conn:
            # Parse license plate to extract state and number
            license_plate_state = None
            license_plate_number = None
            
            if license_plate and len(license_plate.strip()) > 0:
                license_plate = license_plate.strip().upper()
                if len(license_plate) >= 2:
                    # Assume first 2 characters are state if they're letters
                    potential_state = license_plate[:2]
                    if potential_state.isalpha():
                        license_plate_state = potential_state
                        license_plate_number = license_plate[2:]
                    else:
                        license_plate_number = license_plate
                else:
                    license_plate_number = license_plate
            
            cursor = conn.execute(
                """
                UPDATE parkers 
                SET username = ?, license_plate = ?, license_plate_state = ? 
                WHERE email = ?
                """,
                (username, license_plate_number, license_plate_state, email),
            )
            return cursor.rowcount > 0
    except Exception as e:
        print(f"Error updating parker profile: {e}")
        return False


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
    added_by: int,
    title: str | None = None,
    description: str | None = None,
    owned_by: int | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    address: str | None = None,
    price_per_hour: float = 0.0,
) -> int:
    """Create a new place and return the place ID"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO places (title, description, added_by, owned_by,
                latitude, longitude, address, price_per_hour)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                title,
                description,
                added_by,
                owned_by,
                latitude,
                longitude,
                address,
                price_per_hour,
            ),
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
        "price_per_hour",
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


# License plate report operations
def create_license_plate_report(
    license_plate: str, description: str, reporter_email: str | None = None, space_id: int | None = None
) -> int:
    """Create a new license plate report and return the report ID"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO license_plate_reports (license_plate, description, reporter_email, space_id)
            VALUES (?, ?, ?, ?)
        """,
            (license_plate, description, reporter_email, space_id),
        )
        return cursor.lastrowid or 0


def get_license_plate_reports(limit: int = 100) -> list[dict[str, Any]]:
    """Get all license plate reports"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM license_plate_reports 
            ORDER BY created_at DESC 
            LIMIT ?
        """,
            (limit,),
        )
        return [dict(row) for row in cursor.fetchall()]


# Notification operations
def create_notification(
    user_email: str, title: str, message: str, notification_type: str = "info"
) -> int:
    """Create a new notification and return the notification ID"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO notifications (user_email, title, message, type)
            VALUES (?, ?, ?, ?)
        """,
            (user_email, title, message, notification_type),
        )
        return cursor.lastrowid or 0


def get_user_notifications(user_email: str, unread_only: bool = False) -> list[dict[str, Any]]:
    """Get notifications for a user"""
    with get_db() as conn:
        query = """
            SELECT * FROM notifications 
            WHERE user_email = ?
        """
        params = [user_email]
        
        if unread_only:
            query += " AND is_read = 0"
        
        query += " ORDER BY created_at DESC LIMIT 50"
        
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def mark_notification_read(notification_id: int) -> bool:
    """Mark a notification as read"""
    with get_db() as conn:
        cursor = conn.execute(
            "UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,)
        )
        return cursor.rowcount > 0


def get_unread_notification_count(user_email: str) -> int:
    """Get count of unread notifications for a user"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM notifications WHERE user_email = ? AND is_read = 0",
            (user_email,),
        )
        return cursor.fetchone()[0]
