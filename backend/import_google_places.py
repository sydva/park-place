#!/usr/bin/env python3
"""
Simple script to import parking locations from Google Places API

Usage:
    python import_google_places.py [latitude] [longitude] [radius]

Examples:
    python import_google_places.py 37.7749 -122.4194 2000    # San Francisco
    python import_google_places.py 40.7589 -73.9851 1000     # Times Square, NYC
    python import_google_places.py                           # Default: San Francisco
"""

import asyncio
import sys

from google_places import import_google_places_parking


async def main():
    # Default location: San Francisco downtown
    latitude = 37.7749
    longitude = -122.4194
    radius = 2000  # 2km

    # Parse command line arguments if provided
    if len(sys.argv) >= 3:
        try:
            latitude = float(sys.argv[1])
            longitude = float(sys.argv[2])
            if len(sys.argv) >= 4:
                radius = int(sys.argv[3])
        except (ValueError, IndexError):
            print("Usage: python import_google_places.py [latitude] [longitude] [radius]")
            print("Example: python import_google_places.py 37.7749 -122.4194 2000")
            sys.exit(1)

    print(f"Importing parking spaces near ({latitude}, {longitude}) within {radius}m...")

    # Run the import
    await import_google_places_parking(latitude, longitude, radius)


if __name__ == "__main__":
    asyncio.run(main())
