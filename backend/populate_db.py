#!/usr/bin/env python3
"""
Script to populate the database with diverse test parking spaces, users, and reviews
"""

import random
from typing import TypedDict

from backend import database as db


class UserData(TypedDict):
    email: str
    username: str
    license_plate: str
    user_type: str


class ParkingSpaceData(TypedDict):
    title: str
    description: str
    latitude: float
    longitude: float
    address: str
    price_per_hour: float
    tags: list[str]


class ReviewData(TypedDict):
    rating: int
    description: str


# Test user data - now using unified user system
TEST_USERS: list[UserData] = [
    {
        "email": "john@example.com",
        "username": "john_parker",
        "license_plate": "ABC123",
        "user_type": "parker",
    },
    {
        "email": "sara@example.com",
        "username": "sara_driver",
        "license_plate": "XYZ789",
        "user_type": "parker",
    },
    {
        "email": "mike@example.com",
        "username": "mike_commuter",
        "license_plate": "DEF456",
        "user_type": "parker",
    },
    {
        "email": "garage_owner@example.com",
        "username": "downtown_garage",
        "license_plate": "GRG001",
        "user_type": "parker",
    },
    {
        "email": "homeowner@example.com",
        "username": "driveway_sharer",
        "license_plate": "HOM002",
        "user_type": "parker",
    },
    {
        "email": "business@example.com",
        "username": "office_parking",
        "license_plate": "BIZ003",
        "user_type": "parker",
    },
    {
        "email": "amy@example.com",
        "username": "amy_reviewer",
        "license_plate": "AMY456",
        "user_type": "parker",
    },
    {
        "email": "carlos@example.com",
        "username": "carlos_tech",
        "license_plate": "CAR789",
        "user_type": "parker",
    },
]

# Diverse parking spaces with different amenities, prices, and types
DIVERSE_PARKING_SPACES: list[ParkingSpaceData] = [
    {
        "title": "Premium Downtown Garage - Valet Service",
        "description": "Luxury covered parking with valet service, EV charging, and 24/7 security. Perfect for business meetings and special occasions.",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "address": "123 Market St, San Francisco, CA",
        "price_per_hour": 25.0,
        "tags": [
            "covered",
            "ev-charging",
            "security-camera",
            "24-7-access",
            "valet",
            "disabled-access",
        ],
    },
    {
        "title": "Budget Street Parking - Basic",
        "description": "Simple street parking spot, no frills but gets the job done. Great for quick stops and budget-conscious parkers.",
        "latitude": 37.7599,
        "longitude": -122.4148,
        "address": "456 Mission St, San Francisco, CA",
        "price_per_hour": 0.0,
        "tags": [],
    },
    {
        "title": "Residential Driveway - BART Access",
        "description": "Private driveway in quiet neighborhood, 5-minute walk to BART station. Homeowner provides excellent service.",
        "latitude": 37.7929,
        "longitude": -122.4172,
        "address": "789 California St, San Francisco, CA",
        "price_per_hour": 8.0,
        "tags": ["well-lit", "wide-spaces"],
    },
    {
        "title": "Secure Business Lot - Tech Hub",
        "description": "Monitored parking lot serving the Financial District tech companies. Secure entry/exit with key cards provided.",
        "latitude": 37.7946,
        "longitude": -122.3999,
        "address": "321 Montgomery St, San Francisco, CA",
        "price_per_hour": 15.0,
        "tags": ["covered", "security-camera", "wide-spaces", "disabled-access"],
    },
    {
        "title": "EV Charging Station - Tesla Supercharger",
        "description": "Dedicated EV charging spot with Tesla Supercharger and universal charging options. Solar-powered facility.",
        "latitude": 37.7611,
        "longitude": -122.4350,
        "address": "654 Castro St, San Francisco, CA",
        "price_per_hour": 12.0,
        "tags": ["ev-charging", "covered", "well-lit"],
    },
    {
        "title": "Compact Car Only - Chinatown Alley",
        "description": "Tight spot perfect for small cars and motorcycles. Historic Chinatown location, cash payment preferred.",
        "latitude": 37.7941,
        "longitude": -122.4078,
        "address": "987 Grant Ave, San Francisco, CA",
        "price_per_hour": 5.0,
        "tags": [],
    },
    {
        "title": "Night Owl Special - Restaurant District",
        "description": "Great for dinner and nightlife in North Beach. Lower rates after 8 PM, walking distance to top restaurants.",
        "latitude": 37.8067,
        "longitude": -122.4104,
        "address": "159 Columbus Ave, San Francisco, CA",
        "price_per_hour": 10.0,
        "tags": ["covered", "well-lit", "24-7-access"],
    },
    {
        "title": "Family-Friendly Suburban Spot",
        "description": "Wide driveway space perfect for SUVs and family vehicles. Safe residential area with playground nearby.",
        "latitude": 37.7756,
        "longitude": -122.4664,
        "address": "753 Geary Blvd, San Francisco, CA",
        "price_per_hour": 6.0,
        "tags": ["wide-spaces", "well-lit", "disabled-access"],
    },
    {
        "title": "Event Parking - SOMA Warehouse",
        "description": "Large open lot perfect for concerts, festivals, and sporting events. Shuttle service to downtown available.",
        "latitude": 37.7829,
        "longitude": -122.4007,
        "address": "852 Folsom St, San Francisco, CA",
        "price_per_hour": 18.0,
        "tags": ["wide-spaces", "security-camera", "24-7-access"],
    },
    {
        "title": "Luxury Pacific Heights - City Views",
        "description": "Premium parking with stunning city and bay views. Ideal for special occasions and high-end vehicles.",
        "latitude": 37.7930,
        "longitude": -122.4385,
        "address": "741 Fillmore St, San Francisco, CA",
        "price_per_hour": 30.0,
        "tags": ["covered", "valet", "security-camera", "disabled-access"],
    },
    {
        "title": "Senior-Friendly Community Spot",
        "description": "Easy access parking with minimal walking. Close to medical facilities and senior services.",
        "latitude": 37.7609,
        "longitude": -122.4696,
        "address": "963 Irving St, San Francisco, CA",
        "price_per_hour": 4.0,
        "tags": ["disabled-access", "well-lit", "wide-spaces"],
    },
    {
        "title": "Artist Quarter - Creative District",
        "description": "Bohemian parking spot in the heart of Haight-Ashbury. Support local artists and enjoy vintage shop access.",
        "latitude": 37.7692,
        "longitude": -122.4481,
        "address": "258 Haight St, San Francisco, CA",
        "price_per_hour": 7.0,
        "tags": ["well-lit"],
    },
    {
        "title": "Shopping Paradise - Union Square Premium",
        "description": "Prime shopping location with easy access to all major department stores and boutiques. Validation available.",
        "latitude": 37.7880,
        "longitude": -122.4074,
        "address": "333 Post St, San Francisco, CA",
        "price_per_hour": 22.0,
        "tags": ["covered", "security-camera", "disabled-access", "valet"],
    },
    {
        "title": "Convention Center Hub",
        "description": "Perfect for business travelers and convention attendees. Multiple entrances and easy loading zone access.",
        "latitude": 37.7849,
        "longitude": -122.4014,
        "address": "777 Howard St, San Francisco, CA",
        "price_per_hour": 16.0,
        "tags": ["covered", "wide-spaces", "24-7-access", "disabled-access"],
    },
    {
        "title": "Waterfront Views - Embarcadero",
        "description": "Scenic parking with beautiful Bay views and ferry access. Perfect for tourists and romantic dates.",
        "latitude": 37.7955,
        "longitude": -122.3933,
        "address": "101 Embarcadero, San Francisco, CA",
        "price_per_hour": 14.0,
        "tags": ["well-lit", "security-camera"],
    },
]

# Extended Bay Area parking spaces for broader coverage
BAY_AREA_PARKING_SPACES = [
    # Oakland spaces
    {
        "title": "Downtown Oakland Garage - Lake Merritt",
        "description": "Modern parking structure near Lake Merritt with beautiful lake views. Walking distance to restaurants and BART.",
        "latitude": 37.8044,
        "longitude": -122.2711,
        "address": "1234 Grand Ave, Oakland, CA",
        "price_per_hour": 8.0,
        "tags": ["covered", "security-camera", "well-lit"],
        "verified_only": False,
    },
    {
        "title": "Oakland Airport Long-Term Parking",
        "description": "Secure long-term parking with shuttle service to Oakland International Airport terminals.",
        "latitude": 37.7213,
        "longitude": -122.2200,
        "address": "1 Airport Dr, Oakland, CA",
        "price_per_hour": 3.0,
        "tags": ["covered", "security-camera", "24-7-access", "wide-spaces"],
        "verified_only": True,
    },
    {
        "title": "Jack London Square - Waterfront Dining",
        "description": "Premium parking for waterfront dining and entertainment district. Validated parking available at select restaurants.",
        "latitude": 37.7946,
        "longitude": -122.2776,
        "address": "55 Harrison St, Oakland, CA",
        "price_per_hour": 12.0,
        "tags": ["covered", "valet", "well-lit"],
        "verified_only": True,
    },
    # Berkeley spaces
    {
        "title": "UC Berkeley Campus Visitor Parking",
        "description": "Official university parking for campus visitors, events, and prospective students. Permit required.",
        "latitude": 37.8719,
        "longitude": -122.2585,
        "address": "Berkeley Way, Berkeley, CA",
        "price_per_hour": 6.0,
        "tags": ["security-camera", "disabled-access"],
        "verified_only": True,
    },
    {
        "title": "Berkeley BART Station Commuter Lot",
        "description": "Convenient commuter parking with direct BART access to San Francisco and Peninsula.",
        "latitude": 37.8713,
        "longitude": -122.2685,
        "address": "2160 Shattuck Ave, Berkeley, CA",
        "price_per_hour": 2.0,
        "tags": ["wide-spaces", "well-lit", "24-7-access"],
        "verified_only": False,
    },
    {
        "title": "Telegraph Avenue - Student Quarter",
        "description": "Affordable parking in the heart of Berkeley's student district. Close to shops, cafes, and bookstores.",
        "latitude": 37.8688,
        "longitude": -122.2594,
        "address": "2500 Telegraph Ave, Berkeley, CA",
        "price_per_hour": 4.0,
        "tags": ["well-lit"],
        "verified_only": False,
    },
    # San Jose spaces
    {
        "title": "Silicon Valley Tech Campus - Premium",
        "description": "Executive parking for tech meetings and conferences. EV charging stations and valet service available.",
        "latitude": 37.3382,
        "longitude": -121.8863,
        "address": "1000 N Mathilda Ave, Sunnyvale, CA",
        "price_per_hour": 20.0,
        "tags": ["ev-charging", "covered", "valet", "security-camera"],
        "verified_only": True,
    },
    {
        "title": "San Jose Convention Center",
        "description": "Large capacity parking for conventions, trade shows, and events. Multiple access points and good signage.",
        "latitude": 37.3297,
        "longitude": -121.8892,
        "address": "150 W San Carlos St, San Jose, CA",
        "price_per_hour": 10.0,
        "tags": ["covered", "wide-spaces", "disabled-access", "24-7-access"],
        "verified_only": True,
    },
    {
        "title": "Santana Row Shopping - Luxury District",
        "description": "Upscale shopping and dining district with premium parking amenities. Validation available at participating stores.",
        "latitude": 37.3213,
        "longitude": -121.9464,
        "address": "377 Santana Row, San Jose, CA",
        "price_per_hour": 15.0,
        "tags": ["covered", "valet", "security-camera", "disabled-access"],
        "verified_only": True,
    },
    {
        "title": "San Jose Airport Economy Lot",
        "description": "Budget-friendly airport parking with free shuttle service running every 10 minutes.",
        "latitude": 37.3639,
        "longitude": -121.9289,
        "address": "1701 Airport Blvd, San Jose, CA",
        "price_per_hour": 2.5,
        "tags": ["wide-spaces", "security-camera", "24-7-access"],
        "verified_only": False,
    },
    # Palo Alto spaces
    {
        "title": "Stanford University Medical Center",
        "description": "Hospital visitor and patient parking with covered walkways. Validation available for appointments.",
        "latitude": 37.4323,
        "longitude": -122.1697,
        "address": "300 Pasteur Dr, Stanford, CA",
        "price_per_hour": 8.0,
        "tags": ["covered", "disabled-access", "well-lit"],
        "verified_only": False,
    },
    {
        "title": "Palo Alto Caltrain Station",
        "description": "Commuter parking for Caltrain service to San Francisco and Silicon Valley destinations.",
        "latitude": 37.4431,
        "longitude": -122.1635,
        "address": "95 University Ave, Palo Alto, CA",
        "price_per_hour": 3.0,
        "tags": ["24-7-access", "security-camera"],
        "verified_only": False,
    },
    {
        "title": "University Avenue - Downtown Palo Alto",
        "description": "Premium downtown parking for shopping, dining, and business meetings in Palo Alto's main district.",
        "latitude": 37.4419,
        "longitude": -122.1430,
        "address": "123 University Ave, Palo Alto, CA",
        "price_per_hour": 18.0,
        "tags": ["covered", "well-lit", "disabled-access"],
        "verified_only": True,
    },
    # Fremont/South Bay spaces
    {
        "title": "Fremont BART End Station",
        "description": "Large commuter lot serving the southern end of BART system. Popular with South Bay commuters.",
        "latitude": 37.5576,
        "longitude": -121.9764,
        "address": "2000 BART Way, Fremont, CA",
        "price_per_hour": 1.5,
        "tags": ["wide-spaces", "24-7-access", "well-lit"],
        "verified_only": False,
    },
    {
        "title": "Tesla Fremont Factory - Visitor Parking",
        "description": "Visitor parking for Tesla factory tours and employee guests. All spots equipped with Tesla charging.",
        "latitude": 37.4937,
        "longitude": -121.9552,
        "address": "45500 Fremont Blvd, Fremont, CA",
        "price_per_hour": 5.0,
        "tags": ["ev-charging", "security-camera", "covered"],
        "verified_only": True,
    },
    # Richmond/North Bay spaces
    {
        "title": "Richmond BART Ferry Connection",
        "description": "Multi-modal parking serving BART and ferry connections to San Francisco and Marin County.",
        "latitude": 37.9329,
        "longitude": -122.3533,
        "address": "1700 Bissell Ave, Richmond, CA",
        "price_per_hour": 2.0,
        "tags": ["wide-spaces", "security-camera", "well-lit"],
        "verified_only": False,
    },
    {
        "title": "Point Richmond Historic District",
        "description": "Charming small-town parking in historic Point Richmond with bay views and local shops.",
        "latitude": 37.9063,
        "longitude": -122.3774,
        "address": "139 Park Pl, Richmond, CA",
        "price_per_hour": 4.0,
        "tags": ["well-lit"],
        "verified_only": False,
    },
    # Daly City/Peninsula spaces
    {
        "title": "Daly City BART - SF Gateway",
        "description": "First BART station outside San Francisco with ample parking and bus connections.",
        "latitude": 37.7061,
        "longitude": -122.4690,
        "address": "500 John Daly Blvd, Daly City, CA",
        "price_per_hour": 3.0,
        "tags": ["covered", "security-camera", "24-7-access"],
        "verified_only": False,
    },
    {
        "title": "Westlake Shopping Center - Family Hub",
        "description": "Family-friendly shopping center with wide parking spaces and easy access to stores and dining.",
        "latitude": 37.7008,
        "longitude": -122.4830,
        "address": "1200 Southgate Ave, Daly City, CA",
        "price_per_hour": 0.0,
        "tags": ["wide-spaces", "disabled-access", "well-lit"],
        "verified_only": False,
    },
    # Walnut Creek/East Bay spaces
    {
        "title": "Walnut Creek BART - Suburban Hub",
        "description": "Major suburban BART station with large parking structure serving Contra Costa County commuters.",
        "latitude": 37.9061,
        "longitude": -122.0678,
        "address": "200 Ygnacio Valley Rd, Walnut Creek, CA",
        "price_per_hour": 4.0,
        "tags": ["covered", "security-camera", "disabled-access"],
        "verified_only": False,
    },
    {
        "title": "Broadway Plaza - Upscale Shopping",
        "description": "Premium outdoor shopping center with high-end stores, restaurants, and entertainment options.",
        "latitude": 37.8951,
        "longitude": -122.0585,
        "address": "1275 Broadway Plaza, Walnut Creek, CA",
        "price_per_hour": 12.0,
        "tags": ["covered", "valet", "disabled-access", "security-camera"],
        "verified_only": True,
    },
]

# Realistic review data with varied ratings and detailed comments
SAMPLE_REVIEWS: list[ReviewData] = [
    {
        "rating": 5,
        "description": "Absolutely perfect! The valet service was exceptional and my car was spotless when I returned. Worth every penny for special occasions.",
    },
    {
        "rating": 4,
        "description": "Great location and easy access. Only issue was it took a while to find the entrance, but once there it was smooth sailing.",
    },
    {
        "rating": 5,
        "description": "I park here daily for work and it's been consistently excellent. The security makes me feel safe leaving my car overnight.",
    },
    {
        "rating": 3,
        "description": "Decent spot but a bit pricey for what you get. The space was tight for my SUV but location is convenient.",
    },
    {
        "rating": 5,
        "description": "Amazing EV charging setup! My Tesla was fully charged by the time I finished dinner. The covered parking protected it from rain too.",
    },
    {
        "rating": 2,
        "description": "Really tight space and difficult to maneuver. Only suitable for compact cars. The description should be clearer about size limitations.",
    },
    {
        "rating": 4,
        "description": "Perfect for date night in North Beach! Easy walk to all the restaurants and the spot was well-lit when we returned late.",
    },
    {
        "rating": 5,
        "description": "As a senior citizen, I really appreciated the wide spaces and easy access. No stairs to navigate and close to the medical center.",
    },
    {
        "rating": 4,
        "description": "Great for events! Parked here for a Giants game and the shuttle service to downtown was a nice touch. Will use again.",
    },
    {
        "rating": 3,
        "description": "Beautiful views but very expensive. The location is premium but I'd only use it for special occasions due to the cost.",
    },
    {
        "rating": 1,
        "description": "Terrible experience. The 'free' parking wasn't actually free - had to pay city meter fees. Very misleading description.",
    },
    {
        "rating": 5,
        "description": "Fantastic spot for shopping trips! Right in the heart of Union Square and the validation deal with Macy's saved me money.",
    },
    {
        "rating": 4,
        "description": "Business trip parking was smooth and professional. The key card entry system worked perfectly and location was ideal for meetings.",
    },
    {
        "rating": 5,
        "description": "Love supporting this local homeowner who shares their driveway! Great communication and the BART access is exactly as described.",
    },
    {
        "rating": 3,
        "description": "Okay for the neighborhood but nothing special. Gets the job done for basic parking needs but don't expect any amenities.",
    },
    {
        "rating": 4,
        "description": "The waterfront location is beautiful and perfect for tourists. Easy access to the ferry and pier attractions.",
    },
    {
        "rating": 2,
        "description": "Had trouble with the payment system and no one was available to help. The space itself was fine but the technology needs work.",
    },
    {
        "rating": 5,
        "description": "My go-to spot for Chinatown visits! The owner is friendly and the cash-only policy keeps it simple and affordable.",
    },
    {
        "rating": 4,
        "description": "Convention parking was exactly what I needed. Multiple entrances made it easy to find and the rates were reasonable for downtown.",
    },
    {
        "rating": 1,
        "description": "Arrived to find the space occupied by another vehicle. No contact info provided to resolve the issue. Very frustrating experience.",
    },
]


def populate_database():
    """Populate database with diverse test data including reviews"""
    print("Initializing database...")
    db.init_database()

    print("Creating test users...")
    user_ids: list[int] = []
    for user in TEST_USERS:
        try:
            user_id = db.create_user(
                email=user["email"],
                username=user["username"],
                hashed_password="test_hash_" + user["username"],
                user_type=user["user_type"],
                license_plate=user["license_plate"],
            )
            user_ids.append(user_id)
            print(f"  ✓ Created user: {user['username']} (ID: {user_id})")
        except Exception as e:
            print(f"  ⚠ Failed to create user {user['username']}: {e}")

    print("Creating diverse parking spaces...")
    place_ids: list[int] = []

    if not user_ids:
        print("  ❌ No users created, cannot create parking spaces")
        return

    # Combine both San Francisco and Bay Area spaces
    all_spaces = DIVERSE_PARKING_SPACES + BAY_AREA_PARKING_SPACES
    print(f"  Adding {len(all_spaces)} parking spaces across the Bay Area...")

    for _i, space in enumerate(all_spaces):
        try:
            # Randomly assign each space to a user
            added_by = random.choice(user_ids)

            place_id = db.create_place(
                title=space["title"],
                description=space["description"],
                added_by=added_by,
                latitude=space["latitude"],
                longitude=space["longitude"],
                address=space["address"],
                price_per_hour=space["price_per_hour"],
                tags=space["tags"],
            )
            place_ids.append(place_id)
            print(f"  ✓ Created parking space: {space['title']} (ID: {place_id}) - ${space['price_per_hour']}/hr")
        except Exception as e:
            print(f"  ⚠ Failed to create parking space {space['title']}: {e}")

    print("Adding realistic reviews...")
    if place_ids and user_ids:
        # Add reviews to make the data more realistic
        num_reviews = min(30, len(SAMPLE_REVIEWS))  # Create up to 30 reviews

        for _i in range(num_reviews):
            try:
                place_id = random.choice(place_ids)
                user_id = random.choice(user_ids)
                review_data = random.choice(SAMPLE_REVIEWS)

                # Create place rating
                db.create_place_rating(
                    user_id=user_id,
                    place_id=place_id,
                    rating=review_data["rating"],
                    description=review_data["description"],
                )
                print(f"  ✓ Added review: {review_data['rating']} stars for place {place_id}")
            except Exception as e:
                # Skip if duplicate rating (unique constraint)
                if "UNIQUE constraint failed" not in str(e):
                    print(f"  ⚠ Failed to add review: {e}")

    # Print summary
    print("\n" + "=" * 60)
    print("🎉 DATABASE POPULATION COMPLETE WITH DIVERSE DATA! 🎉")
    print("=" * 60)
    print(f"Total users: {db.get_user_count()}")
    print(f"Total parking spaces: {db.get_place_count()}")

    # Show price range
    print("\nPrice Range:")
    print("  • Free parking: Available")
    print("  • Budget ($4-8/hr): Multiple options")
    print("  • Standard ($10-18/hr): Most popular")
    print("  • Premium ($20-30/hr): Luxury locations")

    print("\nAmenities Available:")
    print("  • EV Charging, Valet Service, 24/7 Security")
    print("  • Covered Parking, Wide Spaces, Disabled Access")
    print("  • Well-lit, Security Cameras")

    print("\nParking Types:")
    print("  • Street parking, Driveways, Garages")
    print("  • Compact car spots, Family-friendly spaces")
    print("  • Business lots, Event parking, Luxury spots")

    print("\nAPI endpoints to test:")
    print("  - GET http://localhost:8000/spaces")
    print("  - GET http://localhost:8000/spaces/nearby?lat=37.7749&lng=-122.4194")
    print("  - GET http://localhost:8000/ratings/places/{place_id}")
    print("\nNow enjoy testing with realistic, diverse parking data! 🚗")


if __name__ == "__main__":
    populate_database()
