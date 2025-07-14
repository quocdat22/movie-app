#!/usr/bin/env python3
"""
Test script for protected movie API endpoints.
Tests authentication, movie ratings, favorites, and watchlist functionality.
"""

import requests
import json
import time
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Test credentials (you'll need to replace these with valid Supabase user credentials)
TEST_USER = {
    "email": "test@example.com",
    "password": "testpassword123"
}

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token: Optional[str] = None
        
    def authenticate(self) -> bool:
        """Authenticate with Supabase and get JWT token."""
        print("🔐 Authenticating...")
        
        # Note: This would typically involve calling Supabase auth
        # For testing, you might need to manually get a token from your frontend
        # or implement a test auth endpoint
        
        print("⚠️  Please manually set auth token for testing")
        print("   You can get this from your browser's dev tools when logged into the frontend")
        
        token = input("Enter JWT token (or press Enter to skip auth tests): ").strip()
        if token:
            self.auth_token = token
            self.session.headers.update({"Authorization": f"Bearer {token}"})
            return True
        return False
    
    def test_health_check(self) -> bool:
        """Test basic API health."""
        print("\n🏥 Testing API health...")
        try:
            response = self.session.get(f"{API_BASE}/health")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.json()}")
                return True
        except Exception as e:
            print(f"   ❌ Error: {e}")
        return False
    
    def test_public_endpoints(self) -> bool:
        """Test public movie endpoints."""
        print("\n🎬 Testing public movie endpoints...")
        
        # Test genres
        try:
            response = self.session.get(f"{API_BASE}/movies/genres")
            print(f"   Genres endpoint: {response.status_code}")
            if response.status_code == 200:
                genres = response.json()
                print(f"   Found {len(genres)} genres")
        except Exception as e:
            print(f"   ❌ Genres error: {e}")
            return False
        
        # Test movie list
        try:
            response = self.session.get(f"{API_BASE}/movies?page=1&per_page=5")
            print(f"   Movies list endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Found {len(data.get('movies', []))} movies")
                return True
        except Exception as e:
            print(f"   ❌ Movies list error: {e}")
        
        return False
    
    def test_movie_rating(self, movie_id: int = 1) -> bool:
        """Test movie rating endpoints."""
        print(f"\n⭐ Testing movie rating for movie {movie_id}...")
        
        if not self.auth_token:
            print("   ⚠️  Skipping - no auth token")
            return False
        
        # Rate movie
        try:
            rating_data = {"rating": 4.5}
            response = self.session.post(
                f"{API_BASE}/movies/{movie_id}/rate?rating=4.5"
            )
            print(f"   Rate movie: {response.status_code}")
            if response.status_code in [200, 201]:
                print(f"   Response: {response.json()}")
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Rating error: {e}")
            return False
        
        # Get rating
        try:
            response = self.session.get(f"{API_BASE}/movies/{movie_id}/rating")
            print(f"   Get rating: {response.status_code}")
            if response.status_code == 200:
                print(f"   Rating: {response.json()}")
                return True
        except Exception as e:
            print(f"   ❌ Get rating error: {e}")
        
        return False
    
    def test_favorites(self, movie_id: int = 1) -> bool:
        """Test movie favorites endpoints."""
        print(f"\n❤️  Testing favorites for movie {movie_id}...")
        
        if not self.auth_token:
            print("   ⚠️  Skipping - no auth token")
            return False
        
        # Add to favorites
        try:
            response = self.session.post(f"{API_BASE}/movies/{movie_id}/favorite")
            print(f"   Add to favorites: {response.status_code}")
            if response.status_code in [200, 201, 409]:  # 409 if already exists
                print(f"   Response: {response.json()}")
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Add favorite error: {e}")
            return False
        
        # Check favorite status
        try:
            response = self.session.get(f"{API_BASE}/movies/{movie_id}/favorite")
            print(f"   Check favorite: {response.status_code}")
            if response.status_code == 200:
                print(f"   Status: {response.json()}")
                return True
        except Exception as e:
            print(f"   ❌ Check favorite error: {e}")
        
        return False
    
    def test_watchlist(self, movie_id: int = 1) -> bool:
        """Test movie watchlist endpoints."""
        print(f"\n📺 Testing watchlist for movie {movie_id}...")
        
        if not self.auth_token:
            print("   ⚠️  Skipping - no auth token")
            return False
        
        # Add to watchlist
        try:
            response = self.session.post(f"{API_BASE}/movies/{movie_id}/watchlist")
            print(f"   Add to watchlist: {response.status_code}")
            if response.status_code in [200, 201, 409]:  # 409 if already exists
                print(f"   Response: {response.json()}")
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Add watchlist error: {e}")
            return False
        
        # Check watchlist status
        try:
            response = self.session.get(f"{API_BASE}/movies/{movie_id}/watchlist")
            print(f"   Check watchlist: {response.status_code}")
            if response.status_code == 200:
                print(f"   Status: {response.json()}")
                return True
        except Exception as e:
            print(f"   ❌ Check watchlist error: {e}")
        
        return False
    
    def test_user_lists(self) -> bool:
        """Test user-specific movie lists."""
        print("\n📋 Testing user movie lists...")
        
        if not self.auth_token:
            print("   ⚠️  Skipping - no auth token")
            return False
        
        lists_to_test = ["favorites", "watchlist", "rated"]
        success_count = 0
        
        for list_name in lists_to_test:
            try:
                response = self.session.get(f"{API_BASE}/movies/{list_name}?page=1&per_page=5")
                print(f"   {list_name.title()} list: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Found {len(data.get('movies', []))} movies in {list_name}")
                    success_count += 1
                else:
                    print(f"   Error: {response.text}")
            except Exception as e:
                print(f"   ❌ {list_name} error: {e}")
        
        return success_count == len(lists_to_test)
    
    def test_user_stats(self) -> bool:
        """Test user statistics endpoint."""
        print("\n📊 Testing user statistics...")
        
        if not self.auth_token:
            print("   ⚠️  Skipping - no auth token")
            return False
        
        try:
            response = self.session.get(f"{API_BASE}/movies/user-stats")
            print(f"   User stats: {response.status_code}")
            if response.status_code == 200:
                stats = response.json()
                print(f"   Stats: {json.dumps(stats, indent=2)}")
                return True
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Stats error: {e}")
        
        return False
    
    def test_enhanced_movie_detail(self, movie_id: int = 1) -> bool:
        """Test enhanced movie detail endpoint with user context."""
        print(f"\n🎬 Testing enhanced movie details for movie {movie_id}...")
        
        try:
            response = self.session.get(f"{API_BASE}/movies/{movie_id}/enhanced")
            print(f"   Enhanced details: {response.status_code}")
            if response.status_code == 200:
                movie = response.json()
                print(f"   Movie: {movie.get('title', 'Unknown')}")
                if self.auth_token:
                    print(f"   User rating: {movie.get('user_rating', 'Not rated')}")
                    print(f"   Is favorite: {movie.get('is_favorite', False)}")
                    print(f"   In watchlist: {movie.get('in_watchlist', False)}")
                return True
            else:
                print(f"   Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Enhanced details error: {e}")
        
        return False
    
    def run_all_tests(self):
        """Run comprehensive test suite."""
        print("🚀 Starting Movie API Test Suite")
        print("=" * 50)
        
        # Test public endpoints first
        public_success = (
            self.test_health_check() and 
            self.test_public_endpoints()
        )
        
        if not public_success:
            print("\n❌ Public endpoints failed. Check if the API server is running.")
            return
        
        # Try to authenticate
        auth_success = self.authenticate()
        
        # Test movie details (works with or without auth)
        self.test_enhanced_movie_detail()
        
        if auth_success:
            # Test protected endpoints
            movie_id = 1  # Test with movie ID 1
            
            self.test_movie_rating(movie_id)
            self.test_favorites(movie_id)
            self.test_watchlist(movie_id)
            self.test_user_lists()
            self.test_user_stats()
        
        print("\n" + "=" * 50)
        print("🎯 Test suite completed!")
        if not auth_success:
            print("💡 To test protected endpoints, run with valid JWT token")

def main():
    """Main test function."""
    tester = APITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
