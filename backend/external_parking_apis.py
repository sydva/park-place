#!/usr/bin/env python3
"""
External Parking APIs Integration Module

This module integrates with various external parking data sources:
- Google Places API (for parking location discovery)
- NYC Open Data (free parking regulations)
- SpotHero API (commercial real-time availability)
- ParkWhiz API (commercial real-time availability)
"""

import asyncio
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx

logger = logging.getLogger(__name__)


@dataclass
class ParkingSpace:
    """Standardized parking space data structure"""

    id: str
    source: str  # 'google', 'nyc', 'spothero', 'parkwhiz', etc.
    name: str
    description: str
    latitude: float
    longitude: float
    address: str
    price_per_hour: float
    available_spots: int | None = None
    total_spots: int | None = None
    is_available: bool = True
    features: list[str] = None
    hours: str | None = None
    phone: str | None = None
    website: str | None = None
    last_updated: datetime | None = None

    def __post_init__(self):
        if self.features is None:
            self.features = []
        if self.last_updated is None:
            self.last_updated = datetime.now()


class GooglePlacesAPI:
    """Google Places API integration for parking location discovery"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"

    async def search_parking_near_location(
        self, latitude: float, longitude: float, radius: int = 1000
    ) -> list[ParkingSpace]:
        """Search for parking locations near coordinates"""

        url = f"{self.base_url}/nearbysearch/json"
        params = {
            "location": f"{latitude},{longitude}",
            "radius": radius,
            "type": "parking",
            "key": self.api_key,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                parking_spaces = []
                for place in data.get("results", []):
                    # Get detailed place information
                    details = await self._get_place_details(place["place_id"])

                    parking_space = ParkingSpace(
                        id=f"google_{place['place_id']}",
                        source="google",
                        name=place["name"],
                        description=details.get("formatted_address", ""),
                        latitude=place["geometry"]["location"]["lat"],
                        longitude=place["geometry"]["location"]["lng"],
                        address=details.get(
                            "formatted_address", place.get("vicinity", "")
                        ),
                        price_per_hour=0.0,  # Google doesn't provide pricing
                        features=self._extract_features(details),
                        hours=details.get("opening_hours", {}).get(
                            "weekday_text", None
                        ),
                        phone=details.get("formatted_phone_number"),
                        website=details.get("website"),
                    )
                    parking_spaces.append(parking_space)

                return parking_spaces

        except Exception as e:
            logger.error(f"Error fetching Google Places data: {e}")
            return []

    async def _get_place_details(self, place_id: str) -> dict[str, Any]:
        """Get detailed information for a place"""
        url = f"{self.base_url}/details/json"
        params = {
            "place_id": place_id,
            "fields": "formatted_address,opening_hours,formatted_phone_number,website,types",
            "key": self.api_key,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                return response.json().get("result", {})
        except Exception as e:
            logger.error(f"Error fetching place details for {place_id}: {e}")
            return {}

    def _extract_features(self, details: dict[str, Any]) -> list[str]:
        """Extract parking features from Google Places details"""
        features = []
        place_types = details.get("types", [])

        # Map Google place types to our features
        type_mapping = {
            "parking": "parking",
            "lodging": "valet",
            "shopping_mall": "covered",
            "hospital": "disabled-access",
            "airport": "security-camera",
        }

        for place_type in place_types:
            if place_type in type_mapping:
                features.append(type_mapping[place_type])

        return features


class NYCOpenDataAPI:
    """NYC Open Data API integration for free parking regulations"""

    def __init__(self):
        self.base_url = "https://data.cityofnewyork.us/resource"

    async def get_parking_regulations(
        self,
        latitude: float,
        longitude: float,
        radius: float = 0.01,  # Degrees, roughly 1km
    ) -> list[ParkingSpace]:
        """Get parking regulations from NYC Open Data"""

        # NYC Parking Regulations dataset
        url = f"{self.base_url}/p7t3-btiq.json"

        # Create bounding box around coordinates
        lat_min = latitude - radius
        lat_max = latitude + radius
        lng_min = longitude - radius
        lng_max = longitude + radius

        params = {
            "$where": f"latitude between {lat_min} and {lat_max} and longitude between {lng_min} and {lng_max}",
            "$limit": 100,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()

                parking_spaces = []
                for i, regulation in enumerate(data):
                    if "latitude" in regulation and "longitude" in regulation:
                        parking_space = ParkingSpace(
                            id=f"nyc_{i}_{regulation.get('objectid', 'unknown')}",
                            source="nyc",
                            name=f"NYC Street Parking - {regulation.get('street_name', 'Unknown')}",
                            description=regulation.get(
                                "sign_description", "Street parking"
                            ),
                            latitude=float(regulation["latitude"]),
                            longitude=float(regulation["longitude"]),
                            address=f"{regulation.get('street_name', '')} {regulation.get('from_street', '')}".strip(),
                            price_per_hour=0.0,  # NYC street parking is often metered, but we'd need another dataset for pricing
                            features=["street-parking"],
                            hours=regulation.get("sign_description", ""),
                        )
                        parking_spaces.append(parking_space)

                return parking_spaces

        except Exception as e:
            logger.error(f"Error fetching NYC Open Data: {e}")
            return []


class SpotHeroAPI:
    """SpotHero API integration (requires API key from SpotHero)"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.spothero.com/v1"  # Placeholder URL

    async def search_parking(
        self,
        latitude: float,
        longitude: float,
        start_time: datetime,
        end_time: datetime,
        radius: int = 1000,
    ) -> list[ParkingSpace]:
        """Search for available parking on SpotHero"""

        # Note: This is a placeholder implementation
        # Actual SpotHero API endpoints and authentication would need to be obtained from SpotHero

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        params = {
            "lat": latitude,
            "lng": longitude,
            "radius": radius,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/spots/search", params=params, headers=headers
                )
                response.raise_for_status()
                data = response.json()

                parking_spaces = []
                for spot in data.get("spots", []):
                    parking_space = ParkingSpace(
                        id=f"spothero_{spot['id']}",
                        source="spothero",
                        name=spot["name"],
                        description=spot["description"],
                        latitude=spot["latitude"],
                        longitude=spot["longitude"],
                        address=spot["address"],
                        price_per_hour=spot["price_per_hour"],
                        available_spots=spot.get("available_spots"),
                        total_spots=spot.get("total_spots"),
                        is_available=spot.get("available", True),
                        features=spot.get("features", []),
                    )
                    parking_spaces.append(parking_space)

                return parking_spaces

        except Exception as e:
            logger.error(f"Error fetching SpotHero data: {e}")
            return []


class ParkingAPIAggregator:
    """Aggregates parking data from multiple sources"""

    def __init__(self):
        self.google_api = None
        self.nyc_api = NYCOpenDataAPI()
        self.spothero_api = None

        # Initialize APIs if keys are available
        if google_key := os.getenv("GOOGLE_PLACES_API_KEY"):
            self.google_api = GooglePlacesAPI(google_key)

        if spothero_key := os.getenv("SPOTHERO_API_KEY"):
            self.spothero_api = SpotHeroAPI(spothero_key)

    async def search_all_sources(
        self,
        latitude: float,
        longitude: float,
        radius: int = 1000,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> list[ParkingSpace]:
        """Search parking from all available sources"""

        all_parking = []

        # Collect tasks for concurrent execution
        tasks = []

        # Google Places API
        if self.google_api:
            tasks.append(
                self.google_api.search_parking_near_location(
                    latitude, longitude, radius
                )
            )

        # NYC Open Data (only for NYC area roughly)
        if 40.4774 <= latitude <= 40.9176 and -74.2591 <= longitude <= -73.7004:
            tasks.append(self.nyc_api.get_parking_regulations(latitude, longitude))

        # SpotHero API
        if self.spothero_api and start_time and end_time:
            tasks.append(
                self.spothero_api.search_parking(
                    latitude, longitude, start_time, end_time, radius
                )
            )

        # Execute all API calls concurrently
        if tasks:
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, list):
                    all_parking.extend(result)
                elif isinstance(result, Exception):
                    logger.error(f"API call failed: {result}")

        # Remove duplicates and sort by distance
        unique_parking = self._deduplicate_parking_spaces(all_parking)
        return self._sort_by_distance(unique_parking, latitude, longitude)

    def _deduplicate_parking_spaces(
        self, parking_spaces: list[ParkingSpace]
    ) -> list[ParkingSpace]:
        """Remove duplicate parking spaces from different sources"""
        unique_spaces = {}

        for space in parking_spaces:
            # Create a key based on location (rounded to ~10 meter precision)
            key = (round(space.latitude, 4), round(space.longitude, 4))

            # Keep the space with the most complete data
            if key not in unique_spaces or len(space.features) > len(
                unique_spaces[key].features
            ):
                unique_spaces[key] = space

        return list(unique_spaces.values())

    def _sort_by_distance(
        self, parking_spaces: list[ParkingSpace], latitude: float, longitude: float
    ) -> list[ParkingSpace]:
        """Sort parking spaces by distance from coordinates"""

        def distance_key(space):
            return (
                (space.latitude - latitude) ** 2 + (space.longitude - longitude) ** 2
            ) ** 0.5

        return sorted(parking_spaces, key=distance_key)


# Example usage
async def main():
    """Example of how to use the parking API aggregator"""
    aggregator = ParkingAPIAggregator()

    # Search for parking near San Francisco downtown
    latitude = 37.7749
    longitude = -122.4194

    parking_spaces = await aggregator.search_all_sources(latitude, longitude)

    print(f"Found {len(parking_spaces)} parking spaces:")
    for space in parking_spaces[:5]:  # Show first 5
        print(f"- {space.name} ({space.source}) - ${space.price_per_hour}/hr")


if __name__ == "__main__":
    asyncio.run(main())
