#!/usr/bin/env python3
"""
Test login flow and diagnose issues
"""
import requests
import time
import sys

BASE_URL = "http://127.0.0.1:5000"
TEST_USERNAME = "user1"
TEST_PASSWORD = "user123"

def test_login_flow():
    session = requests.Session()
    
    print("=" * 60)
    print("1. Testing Index Page (GET /)")
    print("=" * 60)
    try:
        r = session.get(f"{BASE_URL}/")
        print(f"✓ Status: {r.status_code}")
        if "Railway Reservation" in r.text:
            print("✓ Login form found on index page")
        else:
            print("✗ Login form NOT found")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("2. Testing Login (POST /login)")
    print("=" * 60)
    try:
        login_data = {
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        }
        r = session.post(f"{BASE_URL}/login", data=login_data, allow_redirects=False)
        print(f"✓ Status: {r.status_code}")
        print(f"✓ Headers: {dict(r.headers)}")
        if r.status_code == 302:
            redirect_location = r.headers.get('Location')
            print(f"✓ Redirect to: {redirect_location}")
        else:
            print(f"✗ Expected 302 redirect, got {r.status_code}")
            print(f"Response: {r.text[:200]}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("3. Testing Home Page (GET /home)")
    print("=" * 60)
    try:
        r = session.get(f"{BASE_URL}/home", allow_redirects=True)
        print(f"✓ Status: {r.status_code}")
        print(f"✓ URL: {r.url}")
        if "Railway Reservation" in r.text or "home" in r.text.lower():
            print("✓ Home page loaded successfully")
            if "Dashboard" in r.text or "Train" in r.text or "search" in r.text.lower():
                print("✓ Dashboard content found")
            else:
                print("⚠ Limited dashboard content")
        else:
            print("✗ Home page content not found")
            print(f"Response snippet: {r.text[:300]}")
    except Exception as e:
        print(f"✗ Error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("4. Testing Train Search (GET /trains)")
    print("=" * 60)
    try:
        r = session.get(f"{BASE_URL}/trains")
        print(f"✓ Status: {r.status_code}")
        trains = r.json() if r.status_code == 200 else None
        if trains:
            print(f"✓ Found {len(trains)} trains")
        else:
            print(f"Response: {r.text[:200]}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("5. Testing Booking Page (GET /book/1)")
    print("=" * 60)
    try:
        r = session.get(f"{BASE_URL}/book/1")
        print(f"✓ Status: {r.status_code}")
        if "book" in r.text.lower():
            print("✓ Booking page loaded")
        else:
            print("✗ Booking page not found")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("✓ LOGIN FLOW TEST COMPLETE")
    print("=" * 60)
    return True

if __name__ == "__main__":
    print("\n🔍 Testing Railway Reservation System Login Flow\n")
    time.sleep(2)  # Wait for server startup
    try:
        test_login_flow()
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        sys.exit(1)
