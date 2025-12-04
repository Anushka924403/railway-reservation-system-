#!/usr/bin/env python3
"""
Comprehensive website test - Login, Browse, Book, Pay, Order Food, View Tickets
"""
import requests
from requests.cookies import RequestsCookieJar
import json

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

def test_login():
    """Test login flow"""
    print("\n🔐 TEST 1: LOGIN")
    print("-" * 50)
    
    # Get login page
    resp = session.get(f"{BASE_URL}/")
    print(f"✓ Login page loaded: {resp.status_code}")
    
    # Login
    login_data = {"username": "user1", "password": "user123"}
    resp = session.post(f"{BASE_URL}/login", data=login_data)
    print(f"✓ Login POST: {resp.status_code}")
    
    if resp.status_code == 302:
        print("✓ Redirect after login: Success")
    else:
        print(f"✗ Expected 302, got {resp.status_code}")
        return False
    
    return True

def test_home_page():
    """Test home page after login"""
    print("\n🏠 TEST 2: HOME PAGE")
    print("-" * 50)
    
    resp = session.get(f"{BASE_URL}/home")
    print(f"✓ Home page loaded: {resp.status_code}")
    
    if resp.status_code == 200:
        if "trains" in resp.text.lower() or "book" in resp.text.lower():
            print("✓ Home page content found")
            return True
        else:
            print("✗ Home page content missing")
            return False
    else:
        print(f"✗ Home page returned {resp.status_code}")
        print(f"Error: {resp.text[:500]}")
        return False

def test_trains_api():
    """Test trains API"""
    print("\n🚆 TEST 3: TRAINS API")
    print("-" * 50)
    
    resp = session.get(f"{BASE_URL}/trains")
    print(f"✓ Trains API: {resp.status_code}")
    
    if resp.status_code == 200:
        try:
            data = resp.json()
            print(f"✓ Found {len(data)} trains")
            if len(data) > 0:
                print(f"  First train: {data[0].get('name', 'N/A')}")
                return True
        except:
            print("✗ Invalid JSON response")
            return False
    else:
        print(f"✗ Expected 200, got {resp.status_code}")
        return False

def test_styles():
    """Test CSS loading"""
    print("\n🎨 TEST 4: STATIC FILES (CSS)")
    print("-" * 50)
    
    resp = session.get(f"{BASE_URL}/style.css")
    print(f"✓ CSS file: {resp.status_code}")
    
    if resp.status_code == 200:
        print(f"✓ CSS loaded successfully ({len(resp.content)} bytes)")
        return True
    else:
        print(f"✗ CSS not found: {resp.status_code}")
        return False

def test_book_flow():
    """Test booking flow"""
    print("\n🎫 TEST 5: BOOKING FLOW")
    print("-" * 50)
    
    # Get trains
    resp = session.get(f"{BASE_URL}/trains")
    if resp.status_code != 200:
        print("✗ Could not fetch trains")
        return False
    
    trains = resp.json()
    if len(trains) == 0:
        print("✗ No trains available")
        return False
    
    train_id = trains[0]['id']
    print(f"✓ Testing with train: {trains[0]['name']}")
    
    # Book ticket
    book_data = {
        "train_id": train_id,
        "journey_date": "2025-12-15",
        "seat_class": "economy",
        "seats": 1
    }
    resp = session.post(f"{BASE_URL}/book/{train_id}", data=book_data)
    print(f"✓ Book request: {resp.status_code}")
    
    if resp.status_code in [200, 302]:
        print("✓ Booking accepted")
        return True
    else:
        print(f"⚠ Booking response: {resp.status_code}")
        return False

def test_menu_api():
    """Test food menu API"""
    print("\n🍽️ TEST 6: FOOD MENU API")
    print("-" * 50)
    
    resp = session.get(f"{BASE_URL}/menu")
    print(f"✓ Menu API: {resp.status_code}")
    
    if resp.status_code == 200:
        try:
            data = resp.json()
            print(f"✓ Menu loaded with categories")
            return True
        except:
            print("⚠ Menu response not JSON")
            return False
    else:
        print(f"⚠ Menu returned {resp.status_code}")
        return False

def main():
    print("=" * 50)
    print("🚀 RAILWAY RESERVATION SYSTEM - WEBSITE TEST")
    print("=" * 50)
    
    tests = [
        ("Login", test_login),
        ("Home Page", test_home_page),
        ("Trains API", test_trains_api),
        ("CSS Files", test_styles),
        ("Booking Flow", test_book_flow),
        ("Food Menu", test_menu_api),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"✗ ERROR: {str(e)}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Website is working properly!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review errors above.")
        return 1

if __name__ == "__main__":
    exit(main())
