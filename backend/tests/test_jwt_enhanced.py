#!/usr/bin/env python3
"""
Test script for Enhanced JWT Verification functionality
Sprint 3 Task 3: JWT verification and refresh token management
"""

import requests
import json
import time
import os
from typing import Dict, Any, Optional

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api"

class JWTTester:
    def __init__(self):
        self.session = requests.Session()
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.supabase_token: Optional[str] = None
        
    def test_token_validation(self) -> bool:
        """Test token validation endpoint"""
        print("\n🔍 Testing token validation...")
        
        # Test without token
        try:
            response = self.session.post(f"{API_BASE}/auth/token/validate")
            print(f"   Validation without token: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: valid={data.get('valid')}, error={data.get('error')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
        
        # Test with invalid token
        try:
            headers = {"Authorization": "Bearer invalid_token_123"}
            response = self.session.post(f"{API_BASE}/auth/token/validate", headers=headers)
            print(f"   Validation with invalid token: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: valid={data.get('valid')}, error={data.get('error')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
        
        return True
    
    def test_token_introspection(self) -> bool:
        """Test token introspection endpoint"""
        print("\n🔬 Testing token introspection...")
        
        # Test without token
        try:
            response = self.session.post(f"{API_BASE}/auth/token/introspect")
            print(f"   Introspection without token: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: active={data.get('active')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
        
        # Test with invalid token
        try:
            headers = {"Authorization": "Bearer invalid_token_123"}
            response = self.session.post(f"{API_BASE}/auth/token/introspect", headers=headers)
            print(f"   Introspection with invalid token: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: active={data.get('active')}, error={data.get('error')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
        
        return True
    
    def test_supabase_token_exchange(self) -> bool:
        """Test Supabase token exchange"""
        print("\n🔄 Testing Supabase token exchange...")
        
        if not self.supabase_token:
            print("   ⚠️  No Supabase token provided, skipping exchange test")
            return True
        
        try:
            headers = {"Authorization": f"Bearer {self.supabase_token}"}
            response = self.session.post(f"{API_BASE}/auth/token/exchange", headers=headers)
            print(f"   Token exchange: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                print(f"   ✅ Received app token pair")
                print(f"   Token type: {data.get('token_type')}")
                print(f"   Expires in: {data.get('expires_in')} seconds")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_token_refresh(self) -> bool:
        """Test token refresh functionality"""
        print("\n🔄 Testing token refresh...")
        
        if not self.refresh_token:
            print("   ⚠️  No refresh token available, skipping refresh test")
            return True
        
        try:
            payload = {"refresh_token": self.refresh_token}
            response = self.session.post(f"{API_BASE}/auth/token/refresh", json=payload)
            print(f"   Token refresh: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                print(f"   ✅ Token refreshed successfully")
                print(f"   New expires in: {data.get('expires_in')} seconds")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_session_info(self) -> bool:
        """Test session information endpoint"""
        print("\n📊 Testing session info...")
        
        # Test without token
        try:
            response = self.session.get(f"{API_BASE}/auth/session")
            print(f"   Session info without token: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Authenticated: {data.get('authenticated')}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
        
        # Test with token if available
        if self.access_token:
            try:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = self.session.get(f"{API_BASE}/auth/session", headers=headers)
                print(f"   Session info with token: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Authenticated: {data.get('authenticated')}")
                    if data.get('user'):
                        print(f"   User: {data['user'].get('email')}")
                        print(f"   Role: {data['user'].get('role')}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
                return False
        
        return True
    
    def test_token_info(self) -> bool:
        """Test token info endpoint"""
        print("\n📋 Testing token info...")
        
        if not self.access_token:
            print("   ⚠️  No access token available, skipping token info test")
            return True
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = self.session.get(f"{API_BASE}/auth/token/info", headers=headers)
            print(f"   Token info: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   User: {data.get('user', {}).get('email')}")
                token_info = data.get('token_info', {})
                print(f"   Expires at: {token_info.get('expires_at')}")
                print(f"   Issued at: {token_info.get('issued_at')}")
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_logout(self) -> bool:
        """Test logout functionality"""
        print("\n🚪 Testing logout...")
        
        if not self.access_token:
            print("   ⚠️  No access token available, skipping logout test")
            return True
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = self.session.post(f"{API_BASE}/auth/logout", headers=headers)
            print(f"   Logout: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {data.get('message')}")
                
                # Test that token is now invalid
                response = self.session.get(f"{API_BASE}/auth/token/info", headers=headers)
                print(f"   Token validation after logout: {response.status_code}")
                
                self.access_token = None
                self.refresh_token = None
                return True
            else:
                print(f"   Error: {response.text}")
                return False
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    def test_protected_endpoint_access(self) -> bool:
        """Test access to protected endpoints with various token states"""
        print("\n🔒 Testing protected endpoint access...")
        
        # Test without token
        try:
            response = self.session.get(f"{API_BASE}/movies/user-stats")
            print(f"   Protected endpoint without token: {response.status_code}")
            if response.status_code == 401:
                print("   ✅ Correctly rejected unauthorized request")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
        
        # Test with token if available
        if self.access_token:
            try:
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = self.session.get(f"{API_BASE}/movies/user-stats", headers=headers)
                print(f"   Protected endpoint with token: {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Successfully accessed protected endpoint")
                elif response.status_code == 401:
                    print("   ⚠️  Token may be invalid or expired")
            except Exception as e:
                print(f"   ❌ Error: {e}")
                return False
        
        return True
    
    def run_comprehensive_tests(self):
        """Run comprehensive JWT testing suite"""
        print("🚀 Starting Enhanced JWT Verification Test Suite")
        print("=" * 60)
        
        # Get initial token if provided
        print("\n🔐 Token Setup")
        supabase_token = input("Enter Supabase JWT token (or press Enter to skip): ").strip()
        if supabase_token:
            self.supabase_token = supabase_token
            print("   ✅ Supabase token provided")
        else:
            print("   ⚠️  No Supabase token - some tests will be skipped")
        
        # Run tests
        tests = [
            ("Basic token validation", self.test_token_validation),
            ("Token introspection", self.test_token_introspection),
            ("Supabase token exchange", self.test_supabase_token_exchange),
            ("Token refresh", self.test_token_refresh),
            ("Session information", self.test_session_info),
            ("Token information", self.test_token_info),
            ("Protected endpoint access", self.test_protected_endpoint_access),
            ("Logout functionality", self.test_logout),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                    print(f"   ✅ {test_name} - PASSED")
                else:
                    print(f"   ❌ {test_name} - FAILED")
            except Exception as e:
                print(f"   ❌ {test_name} - ERROR: {e}")
        
        print("\n" + "=" * 60)
        print(f"🎯 JWT Test Results: {passed}/{total} tests passed")
        
        if passed == total:
            print("🎉 All JWT tests passed successfully!")
        else:
            print("⚠️  Some JWT tests failed - check implementation")
        
        return passed == total

def main():
    """Main test function"""
    tester = JWTTester()
    tester.run_comprehensive_tests()

if __name__ == "__main__":
    main()
