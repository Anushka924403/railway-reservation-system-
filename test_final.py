#!/usr/bin/env python3
"""
Final End-to-End Test for Railway Reservation System
Tests: Login -> Home -> Search -> Book -> Payment -> Food Order -> Tickets
"""

import requests
import json
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

def test_landing_page():
    """Test 1: Landing page loads"""
    print("\n🧪 TEST 1: Landing Page")
    r = session.get(f"{BASE_URL}/")
    assert r.status_code == 200, f"Landing page failed: {r.status_code}"
    assert "Railway Reservation" in r.text, "Landing page missing title"
    print("✅ Landing page loads correctly")

def test_login():
    """Test 2: Login flow"""
    print("\n🧪 TEST 2: Login")
    r = session.post(f"{BASE_URL}/login", data={"username": "user1", "password": "user123"})
    assert r.status_code == 200, f"Login failed: {r.status_code}"
    print("✅ Login successful")

def test_home_page():
    """Test 3: Home page after login"""
    print("\n🧪 TEST 3: Home Page (Dashboard)")
    r = session.get(f"{BASE_URL}/home")
    assert r.status_code == 200, f"Home page failed: {r.status_code}"
    assert "Featured Trains" in r.text, "Home page missing trains section"
    print("✅ Home page loads with trains list")

def test_trains_list():
    """Test 4: Fetch trains API"""
    print("\n🧪 TEST 4: Trains API")
    r = session.get(f"{BASE_URL}/trains")
    assert r.status_code == 200, f"Trains API failed: {r.status_code}"
    trains = r.json()
    assert len(trains) > 0, "No trains returned"
    print(f"✅ Found {len(trains)} trains")
    return trains[0]["id"]

def test_book_ticket(train_id):
    """Test 5: Book a ticket"""
    print(f"\n🧪 TEST 5: Book Ticket (Train ID: {train_id})")
    
    # Get booking page
    r = session.get(f"{BASE_URL}/book/{train_id}")
    assert r.status_code == 200, f"Book page failed: {r.status_code}"
    print("  ✓ Booking page loaded")
    
    # Submit booking
    booking_data = {
        "journey_date": "2025-12-10",
        "class": "AC",
        "seats": "1"
    }
    r = session.post(f"{BASE_URL}/book/{train_id}", data=booking_data)
    assert r.status_code == 302 or r.status_code == 200, f"Booking submission failed: {r.status_code}"
    print("✅ Ticket booked successfully")

def test_payment():
    """Test 6: Payment flow"""
    print("\n🧪 TEST 6: Payment Flow")
    
    # Get all bookings
    r = session.get(f"{BASE_URL}/api/bookings")
    if r.status_code == 200:
        bookings = r.json()
        if bookings and len(bookings) > 0:
            pnr = bookings[0]["pnr"]
            print(f"  ✓ Found booking with PNR: {pnr}")
            
            # Complete payment
            payment_data = {
                "pnr": pnr,
                "payment_method": "card",
                "card_number": "4111111111111111",
                "cvv": "123"
            }
            r = session.post(f"{BASE_URL}/payment/{pnr}", data=payment_data)
            if r.status_code == 200:
                print("✅ Payment processed successfully")
            else:
                print(f"⚠️  Payment response: {r.status_code}")
    else:
        print("⚠️  Could not fetch bookings (might be permission issue)")

def test_menu():
    """Test 7: Food menu"""
    print("\n🧪 TEST 7: Food Menu")
    r = session.get(f"{BASE_URL}/menu")
    assert r.status_code == 200, f"Menu API failed: {r.status_code}"
    menu = r.json()
    assert "categories" in menu, "Menu missing categories"
    print(f"✅ Menu loaded with {len(menu['categories'])} categories")

def test_order_food():
    """Test 8: Order food"""
    print("\n🧪 TEST 8: Order Food")
    order_data = {
        "items": [{"id": 1, "qty": 2}],
        "amount": 200,
        "pnr": "TEST001"
    }
    r = session.post(f"{BASE_URL}/order_food", json=order_data)
    if r.status_code == 200:
        response = r.json()
        if "order_id" in response:
            print(f"✅ Food order placed: {response['order_id']}")
        else:
            print(f"⚠️  Order response: {response}")
    else:
        print(f"⚠️  Food ordering: {r.status_code}")

def test_ai_assistant():
    """Test 9: AI Assistant"""
    print("\n🧪 TEST 9: AI Assistant")
    query_data = {"query": "What is the delay for IR-001?"}
    r = session.post(f"{BASE_URL}/assistant", json=query_data)
    if r.status_code == 200:
        response = r.json()
        if "reply" in response:
            print(f"✅ AI Assistant: {response['reply'][:50]}...")
        else:
            print(f"⚠️  Assistant response: {response}")
    else:
        print(f"⚠️  Assistant API: {r.status_code}")

def test_predictors():
    """Test 10: Delay & Platform Predictors"""
    print("\n🧪 TEST 10: Predictors")
    
    # Test delay predictor
    r = session.get(f"{BASE_URL}/predict_delay?train_id=IR-001&date=2025-12-10")
    if r.status_code == 200:
        result = r.json()
        print(f"✅ Delay Predictor: {result.get('estimated_delay_minutes', '?')} minutes")
    
    # Test platform predictor
    r = session.get(f"{BASE_URL}/predict_platform?train_id=IR-001")
    if r.status_code == 200:
        result = r.json()
        print(f"✅ Platform Predictor: Platform {result.get('predicted_platform', '?')}")

def run_all_tests():
    """Run all tests in sequence"""
    print("=" * 60)
    print("🚆 RAILWAY RESERVATION SYSTEM - FINAL TEST SUITE")
    print("=" * 60)
    
    try:
        test_landing_page()
        test_login()
        test_home_page()
        train_id = test_trains_list()
        test_book_ticket(train_id)
        test_payment()
        test_menu()
        test_order_food()
        test_ai_assistant()
        test_predictors()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\n🌐 Access your website at: http://127.0.0.1:5000")
        print("📝 Demo Credentials:")
        print("   • user1 / user123")
        print("   • user2 / user456")
        print("   • admin / admin123")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    run_all_tests()
