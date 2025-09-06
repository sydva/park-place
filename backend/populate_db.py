#!/usr/bin/env python3
"""
Script to populate the database with test parking spaces
"""

import random

import database as db

# Test user data
TEST_USERS = [
    {"email": "john@example.com", "username": "john_parker", "license_plate": "ABC123"},
    {"email": "sara@example.com", "username": "sara_driver", "license_plate": "XYZ789"},
    {
        "email": "mike@example.com",
        "username": "mike_commuter",
        "license_plate": "DEF456",
    },
]

TEST_PROVIDERS = [
    {"email": "garage_owner@example.com", "username": "downtown_garage"},
    {"email": "homeowner@example.com", "username": "driveway_sharer"},
    {"email": "business@example.com", "username": "office_parking"},
]

# Parking space data around San Francisco (default location)
# Adding more concentrated spaces for better visibility
SF_PARKING_SPACES = [
    {
        "title": "Downtown Garage Spot",
        "description": "Covered parking in downtown SF garage, 24/7 access",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "address": "123 Market St, San Francisco, CA",
    },
    {
        "title": "Mission District Driveway",
        "description": "Private driveway space, walking distance to BART",
        "latitude": 37.7599,
        "longitude": -122.4148,
        "address": "456 Mission St, San Francisco, CA",
    },
    {
        "title": "Nob Hill Street Parking",
        "description": "On-street parking with good access to downtown",
        "latitude": 37.7929,
        "longitude": -122.4172,
        "address": "789 California St, San Francisco, CA",
    },
    {
        "title": "Financial District Lot",
        "description": "Secure parking lot near Financial District",
        "latitude": 37.7946,
        "longitude": -122.3999,
        "address": "321 Montgomery St, San Francisco, CA",
    },
    {
        "title": "Castro Private Spot",
        "description": "Quiet residential area, easy street access",
        "latitude": 37.7611,
        "longitude": -122.4350,
        "address": "654 Castro St, San Francisco, CA",
    },
    {
        "title": "Chinatown Alley Parking",
        "description": "Small spot in Chinatown, perfect for compact cars",
        "latitude": 37.7941,
        "longitude": -122.4078,
        "address": "987 Grant Ave, San Francisco, CA",
    },
    {
        "title": "North Beach Garage",
        "description": "Covered parking near restaurants and nightlife",
        "latitude": 37.8067,
        "longitude": -122.4104,
        "address": "159 Columbus Ave, San Francisco, CA",
    },
    {
        "title": "Richmond Driveway",
        "description": "Residential driveway with easy highway access",
        "latitude": 37.7756,
        "longitude": -122.4664,
        "address": "753 Geary Blvd, San Francisco, CA",
    },
    {
        "title": "SOMA Warehouse Lot",
        "description": "Large open lot, good for events and commuting",
        "latitude": 37.7829,
        "longitude": -122.4007,
        "address": "852 Folsom St, San Francisco, CA",
    },
    {
        "title": "Pacific Heights Spot",
        "description": "Premium location with city views, secure area",
        "latitude": 37.7930,
        "longitude": -122.4385,
        "address": "741 Fillmore St, San Francisco, CA",
    },
    {
        "title": "Sunset District Home",
        "description": "Quiet residential parking, safe neighborhood",
        "latitude": 37.7609,
        "longitude": -122.4696,
        "address": "963 Irving St, San Francisco, CA",
    },
    {
        "title": "Haight-Ashbury Street",
        "description": "Street parking near shops and cafes",
        "latitude": 37.7692,
        "longitude": -122.4481,
        "address": "258 Haight St, San Francisco, CA",
    },
    # Adding more spaces around downtown SF area for better visibility
    {
        "title": "Union Square Garage",
        "description": "Premium parking near Union Square shopping",
        "latitude": 37.7880,
        "longitude": -122.4074,
        "address": "333 Post St, San Francisco, CA",
    },
    {
        "title": "Yerba Buena Lot",
        "description": "Large parking lot near convention center",
        "latitude": 37.7849,
        "longitude": -122.4014,
        "address": "777 Howard St, San Francisco, CA",
    },
    {
        "title": "Embarcadero Spot",
        "description": "Waterfront parking with Bay views",
        "latitude": 37.7955,
        "longitude": -122.3933,
        "address": "101 Embarcadero, San Francisco, CA",
    },
    {
        "title": "Powell Street Garage",
        "description": "Multi-level garage near cable cars",
        "latitude": 37.7870,
        "longitude": -122.4089,
        "address": "432 Powell St, San Francisco, CA",
    },
    {
        "title": "Civic Center Plaza",
        "description": "City hall area parking",
        "latitude": 37.7798,
        "longitude": -122.4180,
        "address": "355 McAllister St, San Francisco, CA",
    },
    {
        "title": "Market Street Meter",
        "description": "Street parking on busy Market Street",
        "latitude": 37.7853,
        "longitude": -122.4056,
        "address": "555 Market St, San Francisco, CA",
    },
    {
        "title": "Moscone Center Garage",
        "description": "Convention center parking garage",
        "latitude": 37.7843,
        "longitude": -122.4013,
        "address": "747 Howard St, San Francisco, CA",
    },
    {
        "title": "AT&T Park Lot",
        "description": "Baseball stadium parking lot",
        "latitude": 37.7786,
        "longitude": -122.3893,
        "address": "24 Willie Mays Plaza, San Francisco, CA",
    },
    # Even more concentrated around typical SF center
    {
        "title": "Pine Street Spot A",
        "description": "Downtown street parking",
        "latitude": 37.7879,
        "longitude": -122.4075,
        "address": "123 Pine St, San Francisco, CA",
    },
    {
        "title": "Pine Street Spot B",
        "description": "Another downtown street spot",
        "latitude": 37.7881,
        "longitude": -122.4077,
        "address": "125 Pine St, San Francisco, CA",
    },
    {
        "title": "Bush Street Parking",
        "description": "Business district parking",
        "latitude": 37.7901,
        "longitude": -122.4089,
        "address": "234 Bush St, San Francisco, CA",
    },
    {
        "title": "Stockton Tunnel Garage",
        "description": "Underground garage near Chinatown",
        "latitude": 37.7884,
        "longitude": -122.4076,
        "address": "444 Stockton St, San Francisco, CA",
    },
    {
        "title": "Kearny Street Lot",
        "description": "Small parking lot in Financial District",
        "latitude": 37.7889,
        "longitude": -122.4042,
        "address": "567 Kearny St, San Francisco, CA",
    },
    {
        "title": "Sutter Street Garage",
        "description": "Multi-story parking garage",
        "latitude": 37.7898,
        "longitude": -122.4086,
        "address": "678 Sutter St, San Francisco, CA",
    },
    {
        "title": "Grant Ave Spot",
        "description": "Chinatown area parking",
        "latitude": 37.7951,
        "longitude": -122.4064,
        "address": "789 Grant Ave, San Francisco, CA",
    },
]


def populate_database():
    """Populate database with test data"""
    print("Initializing database...")
    db.init_database()

    print("Creating test users...")
    parker_ids: list[int] = []
    for user in TEST_USERS:
        try:
            parker_id = db.create_parker(
                email=user["email"],
                username=user["username"],
                hashed_password="test_hash_" + user["username"],
                license_plate=user["license_plate"],
            )
            parker_ids.append(parker_id)
            print(f"  ✓ Created parker: {user['username']} (ID: {parker_id})")
        except Exception as e:
            print(f"  ⚠ Failed to create parker {user['username']}: {e}")

    print("Creating test providers...")
    provider_ids: list[int] = []
    for provider in TEST_PROVIDERS:
        try:
            provider_id = db.create_provider(
                email=provider["email"],
                username=provider["username"],
                hashed_password="test_hash_" + provider["username"],
            )
            provider_ids.append(provider_id)
            print(f"  ✓ Created provider: {provider['username']} (ID: {provider_id})")
        except Exception as e:
            print(f"  ⚠ Failed to create provider {provider['username']}: {e}")

    print("Creating test parking spaces...")
    all_user_ids: list[int] = parker_ids + provider_ids

    if not all_user_ids:
        print("  ❌ No users created, cannot create parking spaces")
        return

    for _i, space in enumerate(SF_PARKING_SPACES):
        try:
            # Randomly assign each space to a user
            added_by = random.choice(all_user_ids)
            owned_by = (
                random.choice(provider_ids)
                if provider_ids and random.random() > 0.3
                else None
            )

            place_id = db.create_place(
                title=str(space["title"]),
                description=str(space["description"]),
                added_by=added_by,
                owned_by=owned_by,
                latitude=float(space["latitude"]),
                longitude=float(space["longitude"]),
                address=str(space["address"]),
            )
            print(f"  ✓ Created parking space: {space['title']} (ID: {place_id})")
        except Exception as e:
            print(f"  ⚠ Failed to create parking space {space['title']}: {e}")

    # Print summary
    print("\n" + "=" * 50)
    print("DATABASE POPULATION COMPLETE")
    print("=" * 50)
    print(f"Total parkers: {db.get_parker_count()}")
    print(f"Total providers: {db.get_provider_count()}")
    print(f"Total parking spaces: {db.get_place_count()}")
    print()
    print("You can now test the app with real data!")
    print("API endpoints:")
    print("  - GET http://localhost:8000/spaces")
    print("  - GET http://localhost:8000/spaces/nearby?lat=37.7749&lng=-122.4194")


if __name__ == "__main__":
    populate_database()
