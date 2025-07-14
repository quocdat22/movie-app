#!/usr/bin/env python3
"""
Test the movies API endpoint as the frontend would call it
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_movies_api_for_frontend():
    """Test the movies API as the frontend would call it"""
    print("🎬 Testing Movies API for Frontend")
    print("=" * 35)
    
    # Test 1: Movies list API
    print("\n1. Testing Movies List API")
    print("-" * 25)
    
    try:
        response = requests.get(f"{BASE_URL}/api/movies?page=1&page_size=20", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Movies returned: {len(data.get('movies', []))}")
            print(f"   ✅ Page: {data.get('page')}")
            print(f"   ✅ Total pages: {data.get('total_pages')}")
            print(f"   ✅ Total movies: {data.get('total')}")
            
            # Show first movie example
            if data.get('movies'):
                first_movie = data['movies'][0]
                print(f"   ✅ First movie: {first_movie.get('title')} ({first_movie.get('release_year')})")
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            print(f"   ❌ Error: {response.json()}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Genres API
    print("\n2. Testing Genres API")
    print("-" * 20)
    
    try:
        response = requests.get(f"{BASE_URL}/api/movies/genres", timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            genres = data.get('data', [])
            print(f"   ✅ Genres returned: {len(genres)}")
            print(f"   ✅ Sample genres: {genres[:5]}")
        else:
            print(f"   ❌ Failed with status: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n🎯 Frontend should now be able to load movies!")
    print("=" * 35)

if __name__ == "__main__":
    test_movies_api_for_frontend()
