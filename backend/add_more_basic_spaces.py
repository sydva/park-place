#!/usr/bin/env python3
"""
Add way more basic spaces and public premium spaces across the Bay Area
"""

import random

import database as db

# Lots more basic spaces - mostly street parking and simple lots
BASIC_SPACES = [
    # San Francisco - tons of street parking with amenities
    {
        "title": "Mission St Street Parking",
        "description": "Basic street parking on busy Mission Street",
        "latitude": 37.7849,
        "longitude": -122.4094,
        "address": "Mission St, San Francisco, CA",
        "price_per_hour": 2.0,
        "tags": ["well-lit"],
        "verified_only": False,
    },
    {
        "title": "Market St Metered Parking",
        "description": "City metered parking along Market Street",
        "latitude": 37.7849,
        "longitude": -122.4094,
        "address": "Market St, San Francisco, CA",
        "price_per_hour": 3.0,
        "tags": ["well-lit", "24-7-access"],
        "verified_only": False,
    },
    {
        "title": "Valencia St Parallel Parking",
        "description": "Street parking in vibrant Valencia corridor",
        "latitude": 37.7599,
        "longitude": -122.4209,
        "address": "Valencia St, San Francisco, CA",
        "price_per_hour": 1.5,
        "tags": ["well-lit"],
        "verified_only": False,
    },
    {
        "title": "Folsom St Basic Spot",
        "description": "Simple street parking spot",
        "latitude": 37.7749,
        "longitude": -122.4094,
        "address": "Folsom St, San Francisco, CA",
        "price_per_hour": 2.5,
        "tags": ["wide-spaces"],
        "verified_only": False,
    },
    {
        "title": "Howard St Parking",
        "description": "SOMA street parking with good lighting",
        "latitude": 37.7849,
        "longitude": -122.4014,
        "address": "Howard St, San Francisco, CA",
        "price_per_hour": 3.5,
        "tags": ["well-lit", "security-camera"],
        "verified_only": False,
    },
    {
        "title": "Van Ness Basic Parking",
        "description": "Street parking on major avenue",
        "latitude": 37.7849,
        "longitude": -122.4236,
        "address": "Van Ness Ave, San Francisco, CA",
        "price_per_hour": 4.0,
        "tags": ["wide-spaces", "well-lit"],
        "verified_only": False,
    },
    {
        "title": "Fillmore St Spot",
        "description": "Street parking in Fillmore district",
        "latitude": 37.7849,
        "longitude": -122.4330,
        "address": "Fillmore St, San Francisco, CA",
        "price_per_hour": 2.0,
        "tags": ["well-lit"],
        "verified_only": False,
    },
    {
        "title": "Polk St Street Parking",
        "description": "Basic city street parking",
        "latitude": 37.7899,
        "longitude": -122.4194,
        "address": "Polk St, San Francisco, CA",
        "price_per_hour": 3.0,
        "tags": ["24-7-access"],
        "verified_only": False,
    },
    {
        "title": "Irving St Residential",
        "description": "Quiet residential street parking",
        "latitude": 37.7599,
        "longitude": -122.4696,
        "address": "Irving St, San Francisco, CA",
        "price_per_hour": 1.0,
        "tags": ["wide-spaces"],
        "verified_only": False,
    },
    {
        "title": "Judah St Parking",
        "description": "Near Golden Gate Park street parking",
        "latitude": 37.7599,
        "longitude": -122.4696,
        "address": "Judah St, San Francisco, CA",
        "price_per_hour": 1.5,
        "tags": ["well-lit"],
        "verified_only": False,
    },
    # Oakland - affordable street parking
    {
        "title": "Broadway Oakland Street",
        "description": "Downtown Oakland street parking",
        "latitude": 37.8044,
        "longitude": -122.2711,
        "address": "Broadway, Oakland, CA",
        "price_per_hour": 2.0,
        "tags": ["well-lit", "24-7-access"],
        "verified_only": False,
    },
    {
        "title": "Telegraph Ave Oakland",
        "description": "Affordable street parking",
        "latitude": 37.8044,
        "longitude": -122.2711,
        "address": "Telegraph Ave, Oakland, CA",
        "price_per_hour": 1.5,
        "tags": ["well-lit"],
        "verified_only": False,
    },
    {
        "title": "International Blvd Spot",
        "description": "Budget parking on International",
        "latitude": 37.7946,
        "longitude": -122.2200,
        "address": "International Blvd, Oakland, CA",
        "price_per_hour": 1.0,
        "tags": ["wide-spaces"],
        "verified_only": False,
    },
    {
        "title": "MacArthur Blvd Parking",
        "description": "Residential area street parking",
        "latitude": 37.8210,
        "longitude": -122.2580,
        "address": "MacArthur Blvd, Oakland, CA",
        "price_per_hour": 1.5,
        "tags": ["well-lit", "wide-spaces"],
        "verified_only": False,
    },
    {
        "title": "Fruitvale Ave Basic",
        "description": "Community street parking",
        "latitude": 37.7946,
        "longitude": -122.2300,
        "address": "Fruitvale Ave, Oakland, CA",
        "price_per_hour": 1.0,
        "tags": ["wide-spaces"],
        "verified_only": False,
    },
    # Berkeley - student-friendly pricing
    {
        "title": "Shattuck Ave Basic",
        "description": "Street parking near downtown Berkeley",
        "latitude": 37.8688,
        "longitude": -122.2694,
        "address": "Shattuck Ave, Berkeley, CA",
        "price_per_hour": 2.0,
        "tags": ["well-lit"],
        "verified_only": False,
    },
    {
        "title": "University Ave Street",
        "description": "Basic street parking",
        "latitude": 37.8719,
        "longitude": -122.2730,
        "address": "University Ave, Berkeley, CA",
        "price_per_hour": 2.5,
        "tags": ["24-7-access"],
        "verified_only": False,
    },
    {
        "title": "College Ave Spot",
        "description": "Quiet residential street",
        "latitude": 37.8563,
        "longitude": -122.2540,
        "address": "College Ave, Berkeley, CA",
        "price_per_hour": 1.5,
        "tags": ["well-lit", "wide-spaces"],
        "verified_only": False,
    },
    {
        "title": "Sacramento St Berkeley",
        "description": "Affordable neighborhood parking",
        "latitude": 37.8719,
        "longitude": -122.2900,
        "address": "Sacramento St, Berkeley, CA",
        "price_per_hour": 1.0,
        "tags": ["wide-spaces"],
        "verified_only": False,
    },
    # San Jose - spread out basic options
    {
        "title": "First St San Jose",
        "description": "Downtown San Jose street parking",
        "latitude": 37.3382,
        "longitude": -121.8863,
        "address": "First St, San Jose, CA",
        "price_per_hour": 2.5,
        "tags": ["well-lit", "24-7-access"],
        "verified_only": False,
    },
    {
        "title": "Santa Clara St Basic",
        "description": "Main street parking",
        "latitude": 37.3297,
        "longitude": -121.8900,
        "address": "Santa Clara St, San Jose, CA",
        "price_per_hour": 3.0,
        "tags": ["well-lit"],
        "verified_only": False,
    },
    {
        "title": "Story Rd Parking",
        "description": "Eastside neighborhood street parking",
        "latitude": 37.3213,
        "longitude": -121.8400,
        "address": "Story Rd, San Jose, CA",
        "price_per_hour": 1.0,
        "tags": ["wide-spaces"],
        "verified_only": False,
    },
    {
        "title": "Alum Rock Ave Basic",
        "description": "Community street parking",
        "latitude": 37.3500,
        "longitude": -121.8200,
        "address": "Alum Rock Ave, San Jose, CA",
        "price_per_hour": 1.0,
        "tags": ["well-lit"],
        "verified_only": False,
    },
    # Peninsula basic spots
    {
        "title": "El Camino Real Parking",
        "description": "Strip mall basic parking",
        "latitude": 37.4419,
        "longitude": -122.1700,
        "address": "El Camino Real, Palo Alto, CA",
        "price_per_hour": 2.0,
        "tags": ["wide-spaces"],
        "verified_only": False,
    },
    {
        "title": "Middlefield Rd Basic",
        "description": "Simple parking lot",
        "latitude": 37.4300,
        "longitude": -122.1100,
        "address": "Middlefield Rd, Palo Alto, CA",
        "price_per_hour": 1.5,
        "tags": ["wide-spaces", "well-lit"],
        "verified_only": False,
    },
    # More East Bay
    {
        "title": "San Pablo Ave Richmond",
        "description": "Basic street parking",
        "latitude": 37.9329,
        "longitude": -122.3400,
        "address": "San Pablo Ave, Richmond, CA",
        "price_per_hour": 1.0,
        "tags": ["well-lit"],
        "verified_only": False,
    },
    {
        "title": "Macdonald Ave Basic",
        "description": "Richmond street parking",
        "latitude": 37.9100,
        "longitude": -122.3200,
        "address": "Macdonald Ave, Richmond, CA",
        "price_per_hour": 1.0,
        "tags": ["wide-spaces"],
        "verified_only": False,
    },
    # South Bay
    {
        "title": "Fremont Blvd Street",
        "description": "Fremont main street parking",
        "latitude": 37.5576,
        "longitude": -121.9800,
        "address": "Fremont Blvd, Fremont, CA",
        "price_per_hour": 1.5,
        "tags": ["well-lit"],
        "verified_only": False,
    },
    {
        "title": "Mowry Ave Basic",
        "description": "Shopping area street parking",
        "latitude": 37.5300,
        "longitude": -122.0200,
        "address": "Mowry Ave, Fremont, CA",
        "price_per_hour": 1.0,
        "tags": ["wide-spaces"],
        "verified_only": False,
    },
]

# Public premium spaces (expensive but don't require verification)
PUBLIC_PREMIUM_SPACES = [
    {
        "title": "Union Square Premium Lot",
        "description": "High-end shopping district premium parking",
        "latitude": 37.7880,
        "longitude": -122.4074,
        "address": "Union Square, San Francisco, CA",
        "price_per_hour": 18.0,
        "tags": ["covered", "security-camera"],
        "verified_only": False,
    },
    {
        "title": "Nob Hill Luxury Parking",
        "description": "Premium hill-top parking with views",
        "latitude": 37.7930,
        "longitude": -122.4161,
        "address": "Nob Hill, San Francisco, CA",
        "price_per_hour": 20.0,
        "tags": ["valet", "covered"],
        "verified_only": False,
    },
    {
        "title": "SOMA Premium Structure",
        "description": "Modern premium parking structure",
        "latitude": 37.7849,
        "longitude": -122.4014,
        "address": "SOMA District, San Francisco, CA",
        "price_per_hour": 16.0,
        "tags": ["covered", "security-camera", "ev-charging"],
        "verified_only": False,
    },
    {
        "title": "Financial District Executive",
        "description": "Business district premium parking",
        "latitude": 37.7946,
        "longitude": -122.3999,
        "address": "Financial District, San Francisco, CA",
        "price_per_hour": 22.0,
        "tags": ["covered", "valet", "security-camera"],
        "verified_only": False,
    },
    # Oakland premium public
    {
        "title": "Jack London Premium Public",
        "description": "Upscale waterfront parking open to all",
        "latitude": 37.7946,
        "longitude": -122.2776,
        "address": "Jack London Square, Oakland, CA",
        "price_per_hour": 15.0,
        "tags": ["covered", "well-lit"],
        "verified_only": False,
    },
    # South Bay premium public
    {
        "title": "San Jose Downtown Premium",
        "description": "Premium downtown parking",
        "latitude": 37.3382,
        "longitude": -121.8900,
        "address": "Downtown San Jose, CA",
        "price_per_hour": 15.0,
        "tags": ["covered", "security-camera"],
        "verified_only": False,
    },
    {
        "title": "Palo Alto Premium Public",
        "description": "High-end Silicon Valley parking",
        "latitude": 37.4419,
        "longitude": -122.1430,
        "address": "Downtown Palo Alto, CA",
        "price_per_hour": 20.0,
        "tags": ["covered", "ev-charging"],
        "verified_only": False,
    },
]


def add_more_spaces():
    # Get existing users
    with db.get_db() as conn:
        cursor = conn.execute("SELECT id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]

    if not user_ids:
        print("No users found in database.")
        return

    print(f"Adding {len(BASIC_SPACES)} basic spaces...")
    basic_count = 0
    for space in BASIC_SPACES:
        try:
            added_by = random.choice(user_ids)
            db.create_place(
                title=str(space["title"]),
                description=str(space["description"]),
                added_by=added_by,
                latitude=float(space["latitude"]),
                longitude=float(space["longitude"]),
                address=str(space["address"]),
                price_per_hour=float(space["price_per_hour"]),
                tags=space["tags"],
                verified_only=space["verified_only"],
            )
            basic_count += 1
            print(f"✓ Added basic: {space['title']} - ${space['price_per_hour']}/hr")
        except Exception as e:
            if "UNIQUE constraint failed" not in str(e):
                print(f"⚠ Failed to add {space['title']}: {e}")

    print(f"\\nAdding {len(PUBLIC_PREMIUM_SPACES)} public premium spaces...")
    premium_count = 0
    for space in PUBLIC_PREMIUM_SPACES:
        try:
            added_by = random.choice(user_ids)
            db.create_place(
                title=str(space["title"]),
                description=str(space["description"]),
                added_by=added_by,
                latitude=float(space["latitude"]),
                longitude=float(space["longitude"]),
                address=str(space["address"]),
                price_per_hour=float(space["price_per_hour"]),
                tags=space["tags"],
                verified_only=space["verified_only"],  # False - public premium
            )
            premium_count += 1
            print(f"✓ Added premium: {space['title']} - ${space['price_per_hour']}/hr")
        except Exception as e:
            if "UNIQUE constraint failed" not in str(e):
                print(f"⚠ Failed to add {space['title']}: {e}")

    print(f"\\n🎉 Added {basic_count} basic spaces and {premium_count} public premium spaces!")
    print(f"Total places now: {db.get_place_count()}")

    # Show new distribution
    print("\\n📊 New Distribution:")
    with db.get_db() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM places WHERE price_per_hour <= 5 AND verified_only = 0")
        public_basic = cursor.fetchone()[0]
        cursor = conn.execute("SELECT COUNT(*) FROM places WHERE price_per_hour >= 15 AND verified_only = 0")
        public_premium = cursor.fetchone()[0]
        cursor = conn.execute("SELECT COUNT(*) FROM places WHERE verified_only = 1")
        verified_only = cursor.fetchone()[0]

    print(f"  • Basic public spaces ($0-5): {public_basic}")
    print(f"  • Premium public spaces ($15+): {public_premium}")
    print(f"  • Verified-only spaces: {verified_only}")
    print("\\nNow unverified users will see lots of basic spaces AND public premium spaces!")


if __name__ == "__main__":
    add_more_spaces()
