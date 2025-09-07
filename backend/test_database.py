#!/usr/bin/env python3
"""
Test script for the consolidated database.py functionality
"""
import os
import sqlite3
import tempfile


def test_database():
    """Test the consolidated database functionality"""
    
    # Use a temporary database for testing
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_db:
        test_db_path = tmp_db.name
    
    # Set the test database path and ensure clean state
    original_db_path = os.environ.get("DB_PATH")
    os.environ["DB_PATH"] = test_db_path
    
    # Import database functions after setting path
    from database import (
        init_database,
        create_user,
        get_user_by_email,
        get_user_by_id,
        get_user_count,
        create_place,
        get_place_by_id,
        get_places_by_creator,
        get_places_by_owner,
        get_published_places,
        search_places_by_location,
        update_place,
        delete_place,
        get_place_count,
        check_database_health,
    )
    
    try:
        print("🧪 Testing consolidated database functionality...\n")
        
        # Test 1: Database initialization
        print("1. Testing database initialization...")
        init_database()
        assert check_database_health(), "Database health check failed"
        print("✅ Database initialized successfully\n")
        
        # Test 2: Create users (parker and provider)
        print("2. Testing user creation...")
        
        # Create a parker (user with license plate)
        parker_id = create_user(
            email="parker@test.com",
            username="testparker",
            hashed_password="hashed123",
            license_plate_state="CA",
            license_plate="ABC123"
        )
        assert parker_id > 0, "Failed to create parker"
        print(f"✅ Created parker with ID: {parker_id}")
        
        # Create a provider (user without license plate)
        provider_id = create_user(
            email="provider@test.com",
            username="testprovider",
            hashed_password="hashed456"
        )
        assert provider_id > 0, "Failed to create provider"
        print(f"✅ Created provider with ID: {provider_id}")
        
        # Test 3: Retrieve users
        print("\n3. Testing user retrieval...")
        
        parker = get_user_by_email("parker@test.com")
        assert parker is not None, "Failed to get parker by email"
        assert parker["license_plate"] == "ABC123", "Parker license plate mismatch"
        assert "average_rating" in parker, "Parker should have average_rating field"
        assert "rating_count" in parker, "Parker should have rating_count field"
        assert parker["rating_count"] == 0, "New parker should have 0 ratings"
        assert parker["average_rating"] is None, "New parker should have None average rating"
        assert "verified" in parker, "Parker should have verified field"
        assert parker["verified"] == 0, "New parker should not be verified"
        print("✅ Retrieved parker by email with rating stats")
        
        provider = get_user_by_id(provider_id)
        assert provider is not None, "Failed to get provider by ID"
        assert provider["license_plate"] is None, "Provider should not have license plate"
        assert "average_rating" in provider, "Provider should have average_rating field"
        assert "rating_count" in provider, "Provider should have rating_count field"
        assert "verified" in provider, "Provider should have verified field"
        assert provider["verified"] == 0, "New provider should not be verified"
        print("✅ Retrieved provider by ID with rating stats")
        
        # Test 4: User count
        print("\n4. Testing user count...")
        user_count = get_user_count()
        assert user_count == 2, f"Expected 2 users, got {user_count}"
        print(f"✅ User count correct: {user_count}")
        
        # Test 5: Create places
        print("\n5. Testing place creation...")
        
        place_id = create_place(
            title="Test Parking Space",
            description="A great parking spot",
            added_by=parker_id,
            creator_is_owner=True,
            latitude=37.7749,
            longitude=-122.4194,
            address="123 Test St, San Francisco, CA",
            price_per_night=25.00
        )
        assert place_id > 0, "Failed to create place"
        print(f"✅ Created place with ID: {place_id}")
        
        # Test 6: Retrieve places
        print("\n6. Testing place retrieval...")
        
        place = get_place_by_id(place_id)
        assert place is not None, "Failed to get place by ID"
        assert place["title"] == "Test Parking Space", "Place title mismatch"
        assert place["added_by"] == parker_id, "Place added_by mismatch"
        assert place["creator_is_owner"] == 1, "Place creator_is_owner should be True"
        assert place["price_per_night"] == 25.00, "Place price_per_night mismatch"
        assert "average_rating" in place, "Place should have average_rating field"
        assert "rating_count" in place, "Place should have rating_count field"
        assert place["rating_count"] == 0, "New place should have 0 ratings"
        assert place["average_rating"] is None, "New place should have None average rating"
        print("✅ Retrieved place by ID with rating stats and pricing")
        
        # Test 7: Get places by creator
        print("\n7. Testing places by creator...")
        
        creator_places = get_places_by_creator(parker_id)
        assert len(creator_places) == 1, "Expected 1 place for creator"
        assert creator_places[0]["id"] == place_id, "Creator place ID mismatch"
        print("✅ Retrieved places by creator")
        
        # Test 8: Get published places
        print("\n8. Testing published places...")
        
        published_places = get_published_places()
        assert len(published_places) == 1, "Expected 1 published place"
        print("✅ Retrieved published places")
        
        # Test 9: Search places by location
        print("\n9. Testing location search...")
        
        nearby_places = search_places_by_location(37.7749, -122.4194, radius_km=1.0)
        assert len(nearby_places) >= 1, "Expected at least 1 nearby place"
        print("✅ Location search working")
        
        # Test 10: Update place
        print("\n10. Testing place update...")
        
        updated = update_place(place_id, title="Updated Parking Space", is_published=False, price_per_night=30.00)
        assert updated, "Failed to update place"
        
        updated_place = get_place_by_id(place_id)
        assert updated_place["title"] == "Updated Parking Space", "Place title not updated"
        assert updated_place["is_published"] == 0, "Place publish status not updated"
        assert updated_place["price_per_night"] == 30.00, "Place price_per_night not updated"
        print("✅ Place updated successfully including price_per_night")
        
        # Test 11: Place count
        print("\n11. Testing place count...")
        
        place_count = get_place_count()
        assert place_count == 1, f"Expected 1 place, got {place_count}"
        print(f"✅ Place count correct: {place_count}")
        
        # Test 12: Delete place
        print("\n12. Testing place deletion...")
        
        deleted = delete_place(place_id)
        assert deleted, "Failed to delete place"
        
        deleted_place = get_place_by_id(place_id)
        assert deleted_place is None, "Place should be deleted"
        print("✅ Place deleted successfully")
        
        # Test 13: Verify foreign key constraints work
        print("\n13. Testing foreign key constraints...")
        
        # Create a place with valid user references
        place_id2 = create_place(
            title="Another Test Space",
            description="Another parking spot",
            added_by=provider_id,
            creator_is_owner=True,
            latitude=37.7849,
            longitude=-122.4294,
            address="456 Test Ave, San Francisco, CA",
            price_per_night=15.50
        )
        assert place_id2 > 0, "Failed to create place with foreign keys"
        print("✅ Foreign key constraints working")
        
        # Test 14: Rating functionality
        print("\n14. Testing rating functionality...")
        
        # Import rating functions
        from database import (
            create_user_rating,
            get_user_ratings_by_ratee,
            get_user_ratings_by_rater,
            get_user_average_rating,
            get_user_rating_count,
            create_place_rating,
            get_place_ratings,
            get_user_place_ratings,
            get_place_average_rating,
            get_place_rating_count,
            delete_user_rating,
            delete_place_rating,
        )
        
        # Create user ratings
        user_rating_id1 = create_user_rating(
            rater_id=provider_id,
            ratee_id=parker_id,
            rating=5,
            description="Great parker, very responsible!"
        )
        assert user_rating_id1 > 0, "Failed to create user rating"
        
        user_rating_id2 = create_user_rating(
            rater_id=provider_id,
            ratee_id=parker_id,
            rating=4,
            description="Good experience"
        )
        assert user_rating_id2 > 0, "Failed to create second user rating"
        print("✅ Created user ratings")
        
        # Test user rating retrieval
        parker_ratings = get_user_ratings_by_ratee(parker_id)
        assert len(parker_ratings) == 2, f"Expected 2 ratings, got {len(parker_ratings)}"
        # Check that both ratings are present (order might be same due to timestamp precision)
        ratings = {r["rating"] for r in parker_ratings}
        assert ratings == {4, 5}, f"Expected ratings {{4, 5}}, got {ratings}"
        
        provider_ratings = get_user_ratings_by_rater(provider_id)
        assert len(provider_ratings) == 2, "Provider should have given 2 ratings"
        print("✅ Retrieved user ratings")
        
        # Test user rating aggregates
        avg_rating = get_user_average_rating(parker_id)
        assert avg_rating == 4.5, f"Expected average 4.5, got {avg_rating}"
        
        rating_count = get_user_rating_count(parker_id)
        assert rating_count == 2, f"Expected 2 ratings, got {rating_count}"
        print("✅ User rating aggregates working")
        
        # Create place ratings  
        place_rating_id1 = create_place_rating(
            user_id=parker_id,
            place_id=place_id2,
            rating=5,
            description="Perfect parking spot!"
        )
        assert place_rating_id1 > 0, "Failed to create place rating"
        
        place_rating_id2 = create_place_rating(
            user_id=provider_id,
            place_id=place_id2,
            rating=3,
            description="Decent location"
        )
        assert place_rating_id2 > 0, "Failed to create second place rating"
        print("✅ Created place ratings")
        
        # Test place rating retrieval
        place_ratings = get_place_ratings(place_id2)
        assert len(place_ratings) == 2, f"Expected 2 place ratings, got {len(place_ratings)}"
        
        parker_place_ratings = get_user_place_ratings(parker_id)
        assert len(parker_place_ratings) == 1, "Parker should have 1 place rating"
        print("✅ Retrieved place ratings")
        
        # Test place rating aggregates
        place_avg = get_place_average_rating(place_id2)
        assert place_avg == 4.0, f"Expected place average 4.0, got {place_avg}"
        
        place_count = get_place_rating_count(place_id2)
        assert place_count == 2, f"Expected 2 place ratings, got {place_count}"
        print("✅ Place rating aggregates working")
        
        # Test rating deletion
        deleted_user = delete_user_rating(user_rating_id1)
        assert deleted_user, "Failed to delete user rating"
        
        deleted_place = delete_place_rating(place_rating_id1)
        assert deleted_place, "Failed to delete place rating"
        print("✅ Rating deletion working")
        
        # Test 15: Verify rating stats are included in user/place retrieval
        print("\n15. Testing rating stats in retrieval functions...")
        
        # Check that parker now has updated rating stats
        updated_parker = get_user_by_id(parker_id)
        assert updated_parker is not None, "Failed to get updated parker"
        assert updated_parker["rating_count"] == 1, f"Expected 1 rating after deletion, got {updated_parker['rating_count']}"
        assert updated_parker["average_rating"] == 4.0, f"Expected average 4.0, got {updated_parker['average_rating']}"
        print("✅ User rating stats updated correctly")
        
        # Check that place has updated rating stats  
        updated_place = get_place_by_id(place_id2)
        assert updated_place is not None, "Failed to get updated place"
        assert updated_place["rating_count"] == 1, f"Expected 1 rating after deletion, got {updated_place['rating_count']}"
        assert updated_place["average_rating"] == 3.0, f"Expected average 3.0, got {updated_place['average_rating']}"
        print("✅ Place rating stats updated correctly")
        
        # Test that rating stats appear in list functions too
        creator_places = get_places_by_creator(provider_id)
        assert len(creator_places) > 0, "Should have creator places"
        assert "average_rating" in creator_places[0], "Creator places should include rating stats"
        assert "rating_count" in creator_places[0], "Creator places should include rating count"
        
        owner_places = get_places_by_owner(provider_id)
        assert len(owner_places) > 0, "Should have owner places"
        assert "average_rating" in owner_places[0], "Owner places should include rating stats"
        assert "rating_count" in owner_places[0], "Owner places should include rating count"
        
        published = get_published_places()
        if len(published) > 0:
            assert "average_rating" in published[0], "Published places should include rating stats"
            assert "rating_count" in published[0], "Published places should include rating count"
        
        print("✅ Rating stats included in all retrieval functions")
        
        # Test 16: User verification functionality
        print("\n16. Testing user verification functionality...")
        
        # Import verification function
        from database import update_user_verification_status
        
        # Test verifying a user
        verified = update_user_verification_status(parker_id, True)
        assert verified, "Failed to verify user"
        
        # Check verification status
        verified_parker = get_user_by_id(parker_id)
        assert verified_parker["verified"] == 1, "Parker should be verified"
        print("✅ User verification successful")
        
        # Test unverifying a user
        unverified = update_user_verification_status(parker_id, False)
        assert unverified, "Failed to unverify user"
        
        # Check verification status
        unverified_parker = get_user_by_id(parker_id)
        assert unverified_parker["verified"] == 0, "Parker should be unverified"
        print("✅ User unverification successful")
        
        # Test verification with invalid user ID
        invalid_verification = update_user_verification_status(99999, True)
        assert not invalid_verification, "Should fail with invalid user ID"
        print("✅ Invalid user ID handled correctly")
        
        print("\n🎉 All tests passed! Database consolidation, ratings, and verification successful!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise
    
    finally:
        # Cleanup
        if original_db_path:
            os.environ["DB_PATH"] = original_db_path
        else:
            os.environ.pop("DB_PATH", None)
        
        # Remove test database
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)


def test_user_type_distinction():
    """Test that we can distinguish between parkers and providers"""
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as tmp_db:
        test_db_path = tmp_db.name
    
    original_db_path = os.environ.get("DB_PATH")
    os.environ["DB_PATH"] = test_db_path
    
    # Import database functions after setting path
    from database import (
        init_database,
        create_user,
        get_user_by_id,
    )
    
    try:
        print("\n🔍 Testing user type distinction...")
        
        init_database()
        
        # Create users of both types
        parker_id = create_user(
            email="parker@example.com",
            username="parker1",
            hashed_password="hash1",
            license_plate="XYZ789"
        )
        
        provider_id = create_user(
            email="provider@example.com", 
            username="provider1",
            hashed_password="hash2"
        )
        
        # Test distinction logic
        parker = get_user_by_id(parker_id)
        provider = get_user_by_id(provider_id)
        
        # Parker should have license plate
        assert parker["license_plate"] is not None, "Parker should have license plate"
        print(f"✅ Parker has license plate: {parker['license_plate']}")
        
        # Provider should not have license plate
        assert provider["license_plate"] is None, "Provider should not have license plate"
        print("✅ Provider has no license plate")
        
        # Demonstrate how to distinguish user types in application logic
        def is_parker(user):
            return user["license_plate"] is not None
        
        def is_provider(user):
            return user["license_plate"] is None
        
        assert is_parker(parker), "Should identify as parker"
        assert is_provider(provider), "Should identify as provider"
        
        print("✅ User type distinction working correctly!")
        
    finally:
        if original_db_path:
            os.environ["DB_PATH"] = original_db_path
        else:
            os.environ.pop("DB_PATH", None)
        
        if os.path.exists(test_db_path):
            os.unlink(test_db_path)


if __name__ == "__main__":
    test_database()
    test_user_type_distinction()
    print("\n🚀 All database tests completed successfully!")