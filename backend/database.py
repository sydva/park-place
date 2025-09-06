import sqlite3
import os
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

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
                FOREIGN KEY (added_by) REFERENCES users (id),
                FOREIGN KEY (owned_by) REFERENCES providers (id),
            )
        """)
        
        # Create indexes for better performance
        conn.execute("CREATE INDEX IF NOT EXISTS idx_parkers_email ON parkers(email)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_parkers_username ON parkers(username)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_parkers_license_plate ON parkers(license_plate)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_providers_email ON providers(email)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_providers_username ON providers(username)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_places_latitude ON places(latitude)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_places_longitude ON places(longitude)")
        
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
def create_user(email: str, username: str, hashed_password: str) -> int:
    """Create a new user and return the user ID"""
    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO users (email, username, hashed_password)
            VALUES (?, ?, ?)
        """, (email, username, hashed_password))
        return cursor.lastrowid

def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Get user by email"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT * FROM users WHERE email = ?
        """, (email,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get user by ID"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT * FROM users WHERE id = ?
        """, (user_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_users(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """Get multiple users with pagination"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT * FROM users 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, skip))
        return [dict(row) for row in cursor.fetchall()]

def update_user_active_status(user_id: int, is_active: bool) -> bool:
    """Update user's active status"""
    with get_db() as conn:
        cursor = conn.execute("""
            UPDATE users 
            SET is_active = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (is_active, user_id))
        return cursor.rowcount > 0

def delete_user(user_id: int) -> bool:
    """Delete a user"""
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return cursor.rowcount > 0

# Post CRUD operations
def create_post(title: str, content: str, user_id: int, is_published: bool = False) -> int:
    """Create a new post and return the post ID"""
    with get_db() as conn:
        cursor = conn.execute("""
            INSERT INTO posts (title, content, user_id, is_published)
            VALUES (?, ?, ?, ?)
        """, (title, content, user_id, is_published))
        return cursor.lastrowid

def get_post_by_id(post_id: int) -> Optional[Dict[str, Any]]:
    """Get post by ID"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT * FROM posts WHERE id = ?
        """, (post_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_posts_by_user(user_id: int, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """Get posts by user ID"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT * FROM posts 
            WHERE user_id = ? 
            ORDER BY created_at DESC 
            LIMIT ? OFFSET ?
        """, (user_id, limit, skip))
        return [dict(row) for row in cursor.fetchall()]

def get_published_posts(skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    """Get published posts"""
    with get_db() as conn:
        cursor = conn.execute("""
            SELECT p.*, u.username 
            FROM posts p 
            JOIN users u ON p.user_id = u.id 
            WHERE p.is_published = 1 
            ORDER BY p.created_at DESC 
            LIMIT ? OFFSET ?
        """, (limit, skip))
        return [dict(row) for row in cursor.fetchall()]

def update_post(post_id: int, title: str = None, content: str = None, is_published: bool = None) -> bool:
    """Update a post"""
    updates = []
    params = []
    
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if content is not None:
        updates.append("content = ?")
        params.append(content)
    if is_published is not None:
        updates.append("is_published = ?")
        params.append(is_published)
    
    if not updates:
        return False
    
    updates.append("updated_at = CURRENT_TIMESTAMP")
    params.append(post_id)
    
    with get_db() as conn:
        cursor = conn.execute(f"""
            UPDATE posts 
            SET {', '.join(updates)}
            WHERE id = ?
        """, params)
        return cursor.rowcount > 0

def delete_post(post_id: int) -> bool:
    """Delete a post"""
    with get_db() as conn:
        cursor = conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
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

def get_post_count() -> int:
    """Get total number of posts"""
    with get_db() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM posts")
        return cursor.fetchone()[0]

