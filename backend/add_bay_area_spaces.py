#!/usr/bin/env python3
"""
Add Bay Area parking spaces to existing database
"""

import random

import database as db
from populate_db import BAY_AREA_PARKING_SPACES


def add_bay_area_spaces():
    # Get existing users
    with db.get_db() as conn:
        cursor = conn.execute("SELECT id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]

    if not user_ids:
        print("No users found in database. Please run populate_db.py first.")
        return

    print(f"Found {len(user_ids)} existing users")
    print("Adding Bay Area parking spaces...")

    count = 0
    for space in BAY_AREA_PARKING_SPACES:
        try:
            added_by = random.choice(user_ids)
            place_id = db.create_place(
                title=str(space["title"]),
                description=str(space["description"]),
                added_by=added_by,
                latitude=float(space["latitude"]),
                longitude=float(space["longitude"]),
                address=str(space["address"]),
                price_per_hour=float(space["price_per_hour"]),
                tags=space["tags"],
                verified_only=space.get("verified_only", False),
            )
            count += 1
            print(
                f"✓ Added: {space['title']} (ID: {place_id}) - ${space['price_per_hour']}/hr"
            )
        except Exception as e:
            if "UNIQUE constraint failed" not in str(e):
                print(f"⚠ Failed to add {space['title']}: {e}")

    print(f"\n🎉 Added {count} new Bay Area parking spaces!")
    print(f"Total places now: {db.get_place_count()}")

    # Show geographic distribution
    print("\n📍 Geographic Coverage:")
    print("  • San Francisco: Original + Enhanced")
    print("  • Oakland: Lake Merritt, Jack London Square, Airport")
    print("  • Berkeley: UC Campus, BART, Telegraph Ave")
    print("  • San Jose: Convention Center, Santana Row, Airport")
    print("  • Palo Alto: Stanford Medical, Caltrain, Downtown")
    print("  • Fremont: BART Station, Tesla Factory")
    print("  • Richmond: BART Ferry, Historic District")
    print("  • Daly City: BART Gateway, Shopping Center")
    print("  • Walnut Creek: BART Hub, Broadway Plaza")


if __name__ == "__main__":
    add_bay_area_spaces()
