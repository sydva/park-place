#!/usr/bin/env python3
"""
Test script for database.py

This script tests all functions in the database module to ensure they work correctly.
Run this script to verify the database functionality.
"""

import os
import sqlite3
import tempfile
import sys
from typing import Dict, Any

# Import the database module (assuming it's named database.py in the same directory)
try:
    import database as db
except ImportError:
    print("Error: Could not import database.py. Make sure it's in the same directory.")
    sys.exit(1)


def setup_test_database():
    """Set up a temporary test database"""
    # Create a temporary file for testing
    temp_fd, temp_path = tempfile.mkstemp(suffix='.db')
    os.close(temp_fd)  # Close the file descriptor, we just need the path
    
    # Set the database path for testing
    original_db_path = db.DB_PATH
    db.DB_PATH = temp_path
    
    # Initialize the test database
    db.init_database()
    
    return temp_path, original_db_path


def cleanup_test_database(temp_path: str, original_db_path: str):
    """Clean up the test database"""
    db.DB_PATH = original_db_path
    if os.path.exists(temp_path):
        os.unlink(temp_path)


def test_database_health():
    """Test database health check"""
    print("Testing database health...")
    assert db.check_database_health() == True
    print("✓ Database health check passed")


def test_user_operations():
    """Test user CRUD operations"""
    print("\nTesting user operations...")
    
    # Test creating users
    user1_id = db.create_user("user1@test.com", "user1", "hashed_pass1", "CA", "ABC123")
    user2_id = db.create_user("user2@test.com", "user2", "hashed_pass2")
    user3_id = db.create_user("user3@test.com", "user3", "hashed_pass3", "NY", "XYZ789")
    
    assert user1_id > 0
    assert user2_id > 0
    assert user3_id > 0
    print(f"✓ Created users with IDs: {user1_id}, {user2_id}, {user3_id}")
    
    # Test getting user by email
    user1 = db.get_user_by_email("user1@test.com")
    assert user1 is not None
    print(f"DEBUG: user1 keys: {list(user1.keys())}")
    print(f"DEBUG: user1 data: {user1}")
    assert user1['email'] == "user1@test.com"
    assert user1['username'] == "user1"
    assert user1['license_plate'] == "ABC123"
    assert user1['license_plate_state'] == "CA"
    assert user1['average_rating'] == 0
    assert user1['rating_count'] == 0
    print("✓ Retrieved user by email with correct data")
    
    # Test getting user by ID
    user2 = db.get_user_by_id(user2_id)
    assert user2 is not None
    assert user2['email'] == "user2@test.com"
    assert user2['license_plate'] is None
    assert user2['average_rating'] == 0
    assert user2['rating_count'] == 0
    print("✓ Retrieved user by ID with correct data")
    
    # Test getting non-existent user
    non_user = db.get_user_by_email("nonexistent@test.com")
    assert non_user is None
    print("✓ Non-existent user returns None")
    
    # Test user count
    count = db.get_user_count()
    assert count == 3
    print(f"✓ User count is correct: {count}")
    
    return user1_id, user2_id, user3_id


def test_place_operations(user1_id: int, user2_id: int, user3_id: int):
    """Test place CRUD operations"""
    print("\nTesting place operations...")
    
    # Test creating places
    place1_id = db.create_place(
        title="Test Place 1",
        description="A great parking spot",
        added_by=user1_id,
        is_owned_by_creator=True,
        latitude=37.7749,
        longitude=-122.4194,
        address="123 Test St, San Francisco, CA"
    )
    
    place2_id = db.create_place(
        title="Test Place 2", 
        description="Another parking spot",
        added_by=user2_id,
        is_owned_by_creator=False,
        latitude=40.7128,
        longitude=-74.0060,
        address="456 Test Ave, New York, NY"
    )
    
    place3_id = db.create_place(
        title="Unpublished Place",
        description="Private spot",
        added_by=user3_id,
        is_owned_by_creator=True,
        address="789 Private Rd"
    )
    
    assert place1_id > 0
    assert place2_id > 0 
    assert place3_id > 0
    print(f"✓ Created places with IDs: {place1_id}, {place2_id}, {place3_id}")
    
    # Test getting place by ID
    place1 = db.get_place_by_id(place1_id)
    assert place1 is not None
    assert place1['title'] == "Test Place 1"
    assert place1['added_by'] == user1_id
    assert place1['is_owned_by_creator'] == 1  # SQLite returns 1/0 for boolean
    assert place1['latitude'] == 37.7749
    assert place1['average_rating'] == 0
    assert place1['rating_count'] == 0
    print("✓ Retrieved place by ID with correct data")
    
    # Test getting places by owner (only places where is_owned_by_creator=True)
    user1_places = db.get_places_by_owner(user1_id)
    assert len(user1_places) == 1
    assert user1_places[0]['id'] == place1_id
    assert 'average_rating' in user1_places[0]
    print("✓ Retrieved places by owner")
    
    # Test that user2 has no owned places (because is_owned_by_creator=False for place2)
    user2_places = db.get_places_by_owner(user2_id)
    assert len(user2_places) == 0
    print("✓ User2 has no owned places (correctly filtered by is_owned_by_creator)")
    
    # Test getting published places
    published = db.get_published_places()
    assert len(published) == 3  # All places are published by default
    assert all('average_rating' in place for place in published)
    print("✓ Retrieved published places")
    
    # Test location search
    sf_places = db.search_places_by_location(37.7749, -122.4194, 1.0)
    assert len(sf_places) >= 1
    assert any(place['id'] == place1_id for place in sf_places)
    assert all('average_rating' in place for place in sf_places)
    print("✓ Location search works")
    
    # Test updating place
    success = db.update_place(place3_id, is_published=False, title="Updated Private Place", is_owned_by_creator=False)
    assert success == True
    
    updated_place = db.get_place_by_id(place3_id)
    assert updated_place['is_published'] == 0
    assert updated_place['title'] == "Updated Private Place"
    assert updated_place['is_owned_by_creator'] == 0
    print("✓ Updated place successfully")
    
    # Test place count
    count = db.get_place_count()
    assert count == 3
    print(f"✓ Place count is correct: {count}")
    
    return place1_id, place2_id, place3_id


def test_user_ratings(user1_id: int, user2_id: int, user3_id: int):
    """Test user rating operations"""
    print("\nTesting user ratings...")
    
    # Create some user ratings
    rating1_id = db.create_user_rating(user1_id, user2_id, 5, "Great user!")
    rating2_id = db.create_user_rating(user3_id, user2_id, 4, "Pretty good")
    rating3_id = db.create_user_rating(user1_id, user2_id, 3, "Another rating")  # Same user rating again
    
    assert rating1_id > 0
    assert rating2_id > 0
    assert rating3_id > 0
    print(f"✓ Created user ratings with IDs: {rating1_id}, {rating2_id}, {rating3_id}")
    
    # Check that user2 now has ratings
    user2 = db.get_user_by_id(user2_id)
    assert user2['rating_count'] == 3
    assert user2['average_rating'] == 4.0  # (5 + 4 + 3) / 3 = 4.0
    print(f"✓ User2 has correct average rating: {user2['average_rating']} from {user2['rating_count']} ratings")
    
    # Check that user1 and user3 have no ratings
    user1 = db.get_user_by_id(user1_id)
    user3 = db.get_user_by_id(user3_id)
    assert user1['rating_count'] == 0
    assert user3['rating_count'] == 0
    print("✓ Users with no ratings have count=0")


def test_place_ratings(user1_id: int, user2_id: int, user3_id: int, place1_id: int, place2_id: int):
    """Test place rating operations"""
    print("\nTesting place ratings...")
    
    # Create some place ratings
    rating1_id = db.create_place_rating(user1_id, place1_id, 5, "Amazing spot!")
    rating2_id = db.create_place_rating(user2_id, place1_id, 4)  # No description
    rating3_id = db.create_place_rating(user3_id, place1_id, 3, "OK place")
    rating4_id = db.create_place_rating(user1_id, place2_id, 2, "Not great")
    
    assert rating1_id > 0
    assert rating2_id > 0
    assert rating3_id > 0
    assert rating4_id > 0
    print(f"✓ Created place ratings with IDs: {rating1_id}, {rating2_id}, {rating3_id}, {rating4_id}")
    
    # Check place1 ratings
    place1 = db.get_place_by_id(place1_id)
    assert place1['rating_count'] == 3
    assert place1['average_rating'] == 4.0  # (5 + 4 + 3) / 3 = 4.0
    print(f"✓ Place1 has correct average rating: {place1['average_rating']} from {place1['rating_count']} ratings")
    
    # Check place2 ratings
    place2 = db.get_place_by_id(place2_id)
    assert place2['rating_count'] == 1
    assert place2['average_rating'] == 2.0
    print(f"✓ Place2 has correct average rating: {place2['average_rating']} from {place2['rating_count']} ratings")
    
    # Verify ratings show up in place lists
    published_places = db.get_published_places()
    place1_in_list = next(p for p in published_places if p['id'] == place1_id)
    assert place1_in_list['average_rating'] == 4.0
    assert place1_in_list['rating_count'] == 3
    print("✓ Ratings appear correctly in place lists")


def test_edge_cases():
    """Test edge cases and error conditions"""
    print("\nTesting edge cases...")
    
    # Test with invalid IDs
    invalid_user = db.get_user_by_id(99999)
    assert invalid_user is None
    
    invalid_place = db.get_place_by_id(99999)
    assert invalid_place is None
    print("✓ Invalid IDs return None")
    
    # Test empty results
    empty_places = db.get_places_by_owner(99999)
    assert len(empty_places) == 0
    
    # Test location search with no results
    empty_location = db.search_places_by_location(0, 0, 0.1)
    # This might return results depending on test data, just make sure it doesn't crash
    assert isinstance(empty_location, list)
    print("✓ Empty result queries work correctly")
    
    # Test updating non-existent place
    update_result = db.update_place(99999, title="Non-existent")
    assert update_result == False
    print("✓ Updating non-existent place returns False")
    
    # Test deleting non-existent place
    delete_result = db.delete_place(99999)
    assert delete_result == False
    print("✓ Deleting non-existent place returns False")


def run_all_tests():
    """Run all tests"""
    print("Setting up test database...")
    temp_path, original_db_path = setup_test_database()
    
    try:
        print("=" * 50)
        print("RUNNING DATABASE TESTS")
        print("=" * 50)
        
        # Run tests
        test_database_health()
        user1_id, user2_id, user3_id = test_user_operations()
        place1_id, place2_id, place3_id = test_place_operations(user1_id, user2_id, user3_id)
        test_user_ratings(user1_id, user2_id, user3_id)
        test_place_ratings(user1_id, user2_id, user3_id, place1_id, place2_id)
        test_edge_cases()
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED! ✅")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        cleanup_test_database(temp_path, original_db_path)
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
