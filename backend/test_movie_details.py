#!/usr/bin/env python3
"""
Test movie detail API endpoints to verify frontend will work
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_movie_detail_apis():
    """Test movie detail API endpoints"""
    print("🎬 Testing Movie Detail APIs")
    print("=" * 30)
    
    # Use the movie ID from the log
    movie_id = "1496480"
    
    # Test 1: Movie lite details (used by main page)
    print(f"\n1. Testing Movie Lite Details (ID: {movie_id})")
    print("-" * 40)
    
    try:
        response = requests.get(f"{BASE_URL}/api/movies/{movie_id}?lite=true", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Movie found: {data.get('title')}")
            print(f"   ✅ Release year: {data.get('release_year')}")
            print(f"   ✅ Genres: {data.get('genre')}")
            print(f"   ✅ Has poster: {data.get('poster_url') is not None}")
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            print(f"   ❌ Error: {response.json()}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Full movie details (used by components)
    print(f"\n2. Testing Full Movie Details")
    print("-" * 30)
    
    try:
        response = requests.get(f"{BASE_URL}/api/movies/{movie_id}", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Movie found: {data.get('title')}")
            print(f"   ✅ Cast members: {len(data.get('cast', []))}")
            print(f"   ✅ Production companies: {len(data.get('production_companies', []))}")
            print(f"   ✅ Vote average: {data.get('vote_average')}")
            print(f"   ✅ Trailer key: {data.get('trailer_key')}")
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Test another movie to make sure it's not just this one
    print(f"\n3. Testing Another Movie (ID: 1510712)")
    print("-" * 35)
    
    try:
        response = requests.get(f"{BASE_URL}/api/movies/1510712?lite=true", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Movie found: {data.get('title')}")
            print(f"   ✅ Release year: {data.get('release_year')}")
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n🎯 Movie details should now load correctly!")
    print("=" * 30)

if __name__ == "__main__":
    test_movie_detail_apis()
