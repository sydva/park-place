#!/usr/bin/env python3
"""
Simple Google Places API integration for parking location discovery
"""

import asyncio
import os
from typing import Any

import database as db
import httpx

# Load environment variables from .env file
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv not installed, just use os.environ
    pass


class GooglePlacesAPI:
    """Simple Google Places API integration to find parking locations"""

    def __init__(self):
        self.api_key = os.getenv("GOOGLE_PLACES_API_KEY")
        if not self.api_key:
            print(
                "Warning: GOOGLE_PLACES_API_KEY not set. Google Places integration disabled."
            )
            self.api_key = None

    async def import_parking_near_location(
        self,
        latitude: float,
        longitude: float,
        radius: int = 2000,
        added_by: int = 1,  # Default user ID
    ) -> int:
        """
        Import parking locations from Google Places API into our database
        Returns the number of spaces added
        """
        if not self.api_key:
            return 0

        try:
            # Search for parking spots using Google Places API
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                "location": f"{latitude},{longitude}",
                "radius": radius,
                "type": "parking",
                "key": self.api_key,
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                spaces_added = 0

                for place in data.get("results", []):
                    # Extract basic info from place
                    place_id = place["place_id"]
                    name = place["name"]
                    location = place["geometry"]["location"]
                    lat = location["lat"]
                    lng = location["lng"]
                    address = place.get("vicinity", "")

                    # Get more details
                    details = await self._get_place_details(place_id)
                    full_address = details.get("formatted_address", address)

                    # Check if we already have this place (by approximate location)
                    existing = db.search_places_by_location(
                        lat, lng, 0.05
                    )  # 50m radius
                    if existing:
                        continue  # Skip duplicates

                    # Determine price (Google doesn't provide this, so we estimate)
                    price_per_hour = self._estimate_price(place, details)

                    # Extract features
                    features = self._extract_features(place, details)

                    # Create the parking space
                    try:
                        db.create_place(
                            title=name,
                            description=f"Parking location from Google Places: {full_address}",
                            added_by=added_by,
                            latitude=lat,
                            longitude=lng,
                            address=full_address,
                            price_per_hour=price_per_hour,
                            tags=features,
                            verified_only=False,  # Google places are public
                        )
                        spaces_added += 1
                        print(f"✓ Added: {name} - ${price_per_hour}/hr")

                    except Exception as e:
                        print(f"⚠ Failed to add {name}: {e}")
                        continue

                return spaces_added

        except Exception as e:
            print(f"Error importing from Google Places: {e}")
            return 0

    async def _get_place_details(self, place_id: str) -> dict[str, Any]:
        """Get additional details for a place"""
        if not self.api_key:
            return {}

        url = "https://maps.googleapis.com/maps/api/place/details/json"
        params = {
            "place_id": place_id,
            "fields": "formatted_address,types,price_level",
            "key": self.api_key,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json().get("result", {})
        except:
            return {}

    def _estimate_price(self, place: dict[str, Any], details: dict[str, Any]) -> float:
        """Estimate parking price based on Google Places data"""

        # Use price_level if available (0-4 scale)
        price_level = details.get("price_level")
        if price_level is not None:
            # Map Google's price level to hourly rates
            price_mapping = {0: 0.0, 1: 2.0, 2: 5.0, 3: 10.0, 4: 20.0}
            return price_mapping.get(price_level, 5.0)

        # Estimate based on place type and rating
        rating = place.get("rating", 3.0)

        # Higher rated places tend to be more expensive
        if rating >= 4.5:
            return 8.0
        elif rating >= 4.0:
            return 5.0
        elif rating >= 3.0:
            return 3.0
        else:
            return 1.0

    def _extract_features(
        self, place: dict[str, Any], details: dict[str, Any]
    ) -> list[str]:
        """Extract features from Google Places data"""
        features = []

        # Map Google place types to our features
        types = details.get("types", [])

        if "parking" in types:
            features.append("parking")
        if "lodging" in types:
            features.append("valet")
        if "shopping_mall" in types:
            features.append("covered")
        if "hospital" in types or "school" in types:
            features.append("disabled-access")
        if "airport" in types or "transit_station" in types:
            features.append("security-camera")
        if "gas_station" in types:
            features.append("24-7-access")

        # Default to basic parking if no specific features
        if not features:
            features = ["parking"]

        return features


async def import_google_places_parking(
    latitude: float, longitude: float, radius: int = 2000
):
    """
    Helper function to import parking from Google Places API
    Usage: python -c "import asyncio; from google_places import import_google_places_parking; asyncio.run(import_google_places_parking(37.7749, -122.4194))"
    """
    api = GooglePlacesAPI()
    if not api.api_key:
        print("Please set GOOGLE_PLACES_API_KEY environment variable")
        return

    spaces_added = await api.import_parking_near_location(latitude, longitude, radius)
    print(
        f"\n🎉 Import complete! Added {spaces_added} parking spaces from Google Places"
    )


if __name__ == "__main__":
    # Example usage - import parking for San Francisco downtown
    asyncio.run(import_google_places_parking(37.7749, -122.4194))
