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
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                user_type TEXT DEFAULT 'parker' CHECK(user_type IN ('parker', 'provider', 'both')),
                license_plate_state TEXT CHECK(length(license_plate_state) = 2),
                license_plate TEXT UNIQUE,
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
                creator_is_owner BOOLEAN DEFAULT 1,
                latitude DECIMAL(10, 8),
                longitude DECIMAL(10, 8),
                address TEXT NOT NULL,
                price_per_hour DECIMAL(10, 2) DEFAULT 0,
                is_published BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (added_by) REFERENCES users (id)
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

        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_verifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_email TEXT NOT NULL UNIQUE,
                status TEXT DEFAULT 'pending',
                profile_photo_url TEXT,
                id_document_url TEXT,
                vehicle_registration_url TEXT,
                verification_notes TEXT,
                verified_at TIMESTAMP,
                verified_by TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_email) REFERENCES users (email)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rater_id INTEGER NOT NULL,
                ratee_id INTEGER NOT NULL,
                rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (rater_id) REFERENCES users (id),
                FOREIGN KEY (ratee_id) REFERENCES users (id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS place_ratings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                place_id INTEGER NOT NULL,
                rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (place_id) REFERENCES places (id)
            )
        """)

        # Create indexes for better performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_license_plate ON users(license_plate)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_places_latitude ON places(latitude)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_places_longitude ON places(longitude)")

        # Create indexes for rating tables
        conn.execute("CREATE INDEX IF NOT EXISTS idx_user_ratings_rater ON user_ratings(rater_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_user_ratings_ratee ON user_ratings(ratee_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_place_ratings_user ON place_ratings(user_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_place_ratings_place ON place_ratings(place_id)")

        # Add price_per_hour column if it doesn't exist (for existing databases)
        cursor = conn.cursor()

        # Add price_per_hour column to places
        cursor.execute("PRAGMA table_info(places)")
        places_columns = [column[1] for column in cursor.fetchall()]
        if "price_per_hour" not in places_columns:
            conn.execute("ALTER TABLE places ADD COLUMN price_per_hour DECIMAL(10, 2) DEFAULT 0")

        # Add user_type column to users table if it doesn't exist
        cursor.execute("PRAGMA table_info(users)")
        users_columns = [column[1] for column in cursor.fetchall()]
        if "user_type" not in users_columns:
            conn.execute("ALTER TABLE users ADD COLUMN user_type TEXT DEFAULT 'parker' CHECK(user_type IN ('parker', 'provider', 'both'))")

        # Add tags column to places table if it doesn't exist
        cursor.execute("PRAGMA table_info(places)")
        places_columns = [column[1] for column in cursor.fetchall()]
        if "tags" not in places_columns:
            conn.execute("ALTER TABLE places ADD COLUMN tags TEXT DEFAULT '[]'")

        # Add units_preference column to users table if it doesn't exist
        cursor.execute("PRAGMA table_info(users)")
        users_columns = [column[1] for column in cursor.fetchall()]
        if "units_preference" not in users_columns:
            conn.execute("ALTER TABLE users ADD COLUMN units_preference TEXT DEFAULT 'imperial' CHECK(units_preference IN ('metric', 'imperial'))")

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


# User CRUD operations
def create_user(
    email: str,
    username: str,
    hashed_password: str,
    user_type: str = "parker",
    license_plate_state: str | None = None,
    license_plate: str | None = None,
) -> int:
    """Create a new user and return the user ID"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO users (email, username, hashed_password, user_type,
                license_plate_state, license_plate)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                email,
                username,
                hashed_password,
                user_type,
                license_plate_state,
                license_plate,
            ),
        )
        return cursor.lastrowid or 0


def get_user_by_license_plate(license_plate: str) -> dict[str, Any] | None:
    """Get user by license plate"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM users WHERE license_plate = ?
        """,
            (license_plate,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def get_user_by_email(email: str) -> dict[str, Any] | None:
    """Get user by email with rating statistics"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT u.*,
                   COALESCE(AVG(ur.rating), 0) as average_rating,
                   COUNT(ur.rating) as rating_count
            FROM users u
            LEFT JOIN user_ratings ur ON u.id = ur.ratee_id
            WHERE u.email = ?
            GROUP BY u.id
        """,
            (email,),
        )
        row = cursor.fetchone()
        if row:
            result = dict(row)
            # Convert to proper types
            result["average_rating"] = float(result["average_rating"]) if result["rating_count"] > 0 else None
            return result
        return None


def get_user_by_id(user_id: int) -> dict[str, Any] | None:
    """Get user by ID with rating statistics"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT u.*,
                   COALESCE(AVG(ur.rating), 0) as average_rating,
                   COUNT(ur.rating) as rating_count
            FROM users u
            LEFT JOIN user_ratings ur ON u.id = ur.ratee_id
            WHERE u.id = ?
            GROUP BY u.id
        """,
            (user_id,),
        )
        row = cursor.fetchone()
        if row:
            result = dict(row)
            # Convert to proper types
            result["average_rating"] = float(result["average_rating"]) if result["rating_count"] > 0 else None
            return result
        return None


def update_user(
    email: str,
    username: str | None = None,
    license_plate: str | None = None,
    license_plate_state: str | None = None,
    user_type: str | None = None,
    is_verified: bool | None = None,
    units_preference: str | None = None,
) -> bool:
    """Update user profile by email"""
    # Build the SET clause dynamically based on provided parameters
    updates: list[str] = []
    params: list[Any] = []

    if username is not None:
        updates.append("username = ?")
        params.append(username)
    if license_plate is not None:
        updates.append("license_plate = ?")
        params.append(license_plate)
    if license_plate_state is not None:
        updates.append("license_plate_state = ?")
        params.append(license_plate_state)
    if user_type is not None:
        updates.append("user_type = ?")
        params.append(user_type)
    if is_verified is not None:
        updates.append("is_verified = ?")
        params.append(is_verified)
    if units_preference is not None:
        updates.append("units_preference = ?")
        params.append(units_preference)

    if not updates:
        return True  # No updates requested

    params.append(email)  # For the WHERE clause

    with get_db() as conn:
        cursor = conn.execute(f"UPDATE users SET {', '.join(updates)} WHERE email = ?", params)
        return cursor.rowcount > 0


# Place CRUD operations
def create_place(
    added_by: int,
    title: str | None = None,
    description: str | None = None,
    creator_is_owner: bool = True,
    latitude: float | None = None,
    longitude: float | None = None,
    address: str | None = None,
    price_per_hour: float = 0.0,
    tags: list[str] | None = None,
) -> int:
    """Create a new place and return the place ID"""
    import json

    tags_json = json.dumps(tags or [])

    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO places (title, description, added_by, creator_is_owner,
                latitude, longitude, address, price_per_hour, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                title,
                description,
                added_by,
                creator_is_owner,
                latitude,
                longitude,
                address,
                price_per_hour,
                tags_json,
            ),
        )
        return cursor.lastrowid or 0


def _parse_place_tags(place_dict: dict[str, Any]) -> dict[str, Any]:
    """Helper function to parse tags JSON in place records"""
    import json

    if place_dict and "tags" in place_dict:
        try:
            place_dict["tags"] = json.loads(place_dict["tags"])
        except (json.JSONDecodeError, TypeError):
            place_dict["tags"] = []
    return place_dict


def get_place_by_id(place_id: int) -> dict[str, Any] | None:
    """Get place by ID with rating statistics"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT p.*,
                   COALESCE(AVG(pr.rating), 0) as average_rating,
                   COUNT(pr.rating) as rating_count
            FROM places p
            LEFT JOIN place_ratings pr ON p.id = pr.place_id
            WHERE p.id = ?
            GROUP BY p.id
        """,
            (place_id,),
        )
        row = cursor.fetchone()
        if row:
            result = dict(row)
            # Convert to proper types
            result["average_rating"] = float(result["average_rating"]) if result["rating_count"] > 0 else None
            return _parse_place_tags(result)
        return None


def get_places_by_creator(creator_id: int, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
    """Get places by creator ID with rating statistics"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT p.*,
                   COALESCE(AVG(pr.rating), 0) as average_rating,
                   COUNT(pr.rating) as rating_count
            FROM places p
            LEFT JOIN place_ratings pr ON p.id = pr.place_id
            WHERE p.added_by = ?
            GROUP BY p.id
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        """,
            (creator_id, limit, skip),
        )
        results: list[dict[str, Any]] = []
        for row in cursor.fetchall():
            result = dict(row)
            result["average_rating"] = float(result["average_rating"]) if result["rating_count"] > 0 else None
            results.append(_parse_place_tags(result))
        return results


def get_places_by_owner(owner_id: int, skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
    """Get places owned by a user (where creator_is_owner=True and added_by=owner_id)"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT p.*,
                   COALESCE(AVG(pr.rating), 0) as average_rating,
                   COUNT(pr.rating) as rating_count
            FROM places p
            LEFT JOIN place_ratings pr ON p.id = pr.place_id
            WHERE p.added_by = ? AND p.creator_is_owner = 1
            GROUP BY p.id
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        """,
            (owner_id, limit, skip),
        )
        results: list[dict[str, Any]] = []
        for row in cursor.fetchall():
            result = dict(row)
            result["average_rating"] = float(result["average_rating"]) if result["rating_count"] > 0 else None
            results.append(_parse_place_tags(result))
        return results


def get_published_places(skip: int = 0, limit: int = 100) -> list[dict[str, Any]]:
    """Get published places with rating statistics"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT p.*,
                   COALESCE(AVG(pr.rating), 0) as average_rating,
                   COUNT(pr.rating) as rating_count
            FROM places p
            LEFT JOIN place_ratings pr ON p.id = pr.place_id
            WHERE p.is_published = 1
            GROUP BY p.id
            ORDER BY p.created_at DESC
            LIMIT ? OFFSET ?
        """,
            (limit, skip),
        )
        results: list[dict[str, Any]] = []
        for row in cursor.fetchall():
            result = dict(row)
            result["average_rating"] = float(result["average_rating"]) if result["rating_count"] > 0 else None
            results.append(_parse_place_tags(result))
        return results


def search_places_by_location(lat: float, lng: float, radius_km: float = 1.0) -> list[dict[str, Any]]:
    """Search places within radius of given coordinates with rating statistics"""
    with get_db() as conn:
        # Simple bounding box search (for MVP - in production use PostGIS)
        # 1 degree of latitude ≈ 111 km
        lat_delta = radius_km / 111.0
        # 1 degree of longitude varies by latitude
        import math

        lng_delta = radius_km / (111.0 * math.cos(math.radians(lat)))

        cursor = conn.execute(
            """
            SELECT p.*,
                   COALESCE(AVG(pr.rating), 0) as average_rating,
                   COUNT(pr.rating) as rating_count
            FROM places p
            LEFT JOIN place_ratings pr ON p.id = pr.place_id
            WHERE p.latitude BETWEEN ? AND ?
            AND p.longitude BETWEEN ? AND ?
            AND p.is_published = 1
            GROUP BY p.id
        """,
            (lat - lat_delta, lat + lat_delta, lng - lng_delta, lng + lng_delta),
        )
        results: list[dict[str, Any]] = []
        for row in cursor.fetchall():
            result = dict(row)
            result["average_rating"] = float(result["average_rating"]) if result["rating_count"] > 0 else None
            results.append(_parse_place_tags(result))
        return results


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
        "creator_is_owner",
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


def get_user_count() -> int:
    """Get total number of users"""
    with get_db() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM users")
        return cursor.fetchone()[0]


def get_place_count() -> int:
    """Get total number of places"""
    with get_db() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM places")
        return cursor.fetchone()[0]


# License plate report operations
def create_license_plate_report(
    license_plate: str,
    description: str,
    reporter_email: str | None = None,
    space_id: int | None = None,
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


# User Rating CRUD operations
def create_user_rating(
    rater_id: int,
    ratee_id: int,
    rating: int,
    description: str | None = None,
) -> int:
    """Create a new user rating and return the rating ID"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO user_ratings (rater_id, ratee_id, rating, description)
            VALUES (?, ?, ?, ?)
        """,
            (rater_id, ratee_id, rating, description),
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


def get_user_ratings_by_ratee(ratee_id: int) -> list[dict[str, Any]]:
    """Get all ratings for a specific user (ratee)"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT ur.*, u.username as rater_username
            FROM user_ratings ur
            JOIN users u ON ur.rater_id = u.id
            WHERE ur.ratee_id = ?
            ORDER BY ur.created_at DESC
        """,
            (ratee_id,),
        )
        return [dict(row) for row in cursor.fetchall()]


def get_user_ratings_by_rater(rater_id: int) -> list[dict[str, Any]]:
    """Get all ratings given by a specific user (rater)"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT ur.*, u.username as ratee_username
            FROM user_ratings ur
            JOIN users u ON ur.ratee_id = u.id
            WHERE ur.rater_id = ?
            ORDER BY ur.created_at DESC
        """,
            (rater_id,),
        )
        return [dict(row) for row in cursor.fetchall()]


def get_user_average_rating(user_id: int) -> float | None:
    """Get the average rating for a user"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT AVG(rating) FROM user_ratings WHERE ratee_id = ?
        """,
            (user_id,),
        )
        result = cursor.fetchone()[0]
        return float(result) if result is not None else None


def get_user_rating_count(user_id: int) -> int:
    """Get the total number of ratings for a user"""
    with get_db() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM user_ratings WHERE ratee_id = ?", (user_id,))
        return cursor.fetchone()[0]


# Place Rating CRUD operations
def create_place_rating(
    user_id: int,
    place_id: int,
    rating: int,
    description: str | None = None,
) -> int:
    """Create a new place rating and return the rating ID"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO place_ratings (user_id, place_id, rating, description)
            VALUES (?, ?, ?, ?)
        """,
            (user_id, place_id, rating, description),
        )
        return cursor.lastrowid or 0


# Notification operations
def create_notification(user_email: str, title: str, message: str, notification_type: str = "info") -> int:
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
        cursor = conn.execute("UPDATE notifications SET is_read = 1 WHERE id = ?", (notification_id,))
        return cursor.rowcount > 0


def get_unread_notification_count(user_email: str) -> int:
    """Get count of unread notifications for a user"""
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT COUNT(*) FROM notifications WHERE user_email = ? AND is_read = 0",
            (user_email,),
        )
        return cursor.fetchone()[0]


def get_place_ratings(place_id: int) -> list[dict[str, Any]]:
    """Get all ratings for a specific place"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT pr.*, u.username
            FROM place_ratings pr
            JOIN users u ON pr.user_id = u.id
            WHERE pr.place_id = ?
            ORDER BY pr.created_at DESC
        """,
            (place_id,),
        )
        return [dict(row) for row in cursor.fetchall()]


def get_user_place_ratings(user_id: int) -> list[dict[str, Any]]:
    """Get all place ratings given by a specific user"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT pr.*, p.title as place_title
            FROM place_ratings pr
            JOIN places p ON pr.place_id = p.id
            WHERE pr.user_id = ?
            ORDER BY pr.created_at DESC
        """,
            (user_id,),
        )
        return [dict(row) for row in cursor.fetchall()]


def get_place_average_rating(place_id: int) -> float | None:
    """Get the average rating for a place"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT AVG(rating) FROM place_ratings WHERE place_id = ?
        """,
            (place_id,),
        )
        result = cursor.fetchone()[0]
        return float(result) if result is not None else None


def get_place_rating_count(place_id: int) -> int:
    """Get the total number of ratings for a place"""
    with get_db() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM place_ratings WHERE place_id = ?", (place_id,))
        return cursor.fetchone()[0]


def delete_user_rating(rating_id: int) -> bool:
    """Delete a user rating"""
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM user_ratings WHERE id = ?", (rating_id,))
        return cursor.rowcount > 0


def delete_place_rating(rating_id: int) -> bool:
    """Delete a place rating"""
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM place_ratings WHERE id = ?", (rating_id,))
        return cursor.rowcount > 0


# User verification operations
def create_user_verification(
    user_email: str,
    profile_photo_url: str | None = None,
    id_document_url: str | None = None,
    vehicle_registration_url: str | None = None,
) -> int:
    """Create a new user verification record and return the verification ID"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            INSERT INTO user_verifications (user_email, profile_photo_url, id_document_url, vehicle_registration_url)
            VALUES (?, ?, ?, ?)
        """,
            (user_email, profile_photo_url, id_document_url, vehicle_registration_url),
        )
        return cursor.lastrowid or 0


def get_user_verification(user_email: str) -> dict[str, Any] | None:
    """Get user verification by email"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM user_verifications WHERE user_email = ?
        """,
            (user_email,),
        )
        row = cursor.fetchone()
        return dict(row) if row else None


def update_verification_status(
    user_email: str,
    status: str,
    verified_by: str | None = None,
    verification_notes: str | None = None,
) -> bool:
    """Update verification status"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            UPDATE user_verifications
            SET status = ?, verified_by = ?, verification_notes = ?, verified_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE user_email = ?
        """,
            (status, verified_by, verification_notes, user_email),
        )
        return cursor.rowcount > 0


def get_pending_verifications() -> list[dict[str, Any]]:
    """Get all pending verifications"""
    with get_db() as conn:
        cursor = conn.execute(
            """
            SELECT * FROM user_verifications
            WHERE status = 'pending'
            ORDER BY created_at DESC
        """
        )
        return [dict(row) for row in cursor.fetchall()]
