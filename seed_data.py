#!/usr/bin/env python3
"""Seed the database with sample trains, bookings, and test users."""
from app import app
from models import db, Train, SeatAvailability, User, Booking, Payment
from datetime import datetime, date, timedelta
from werkzeug.security import generate_password_hash
import uuid


def seed_trains():
	"""Add sample trains to the database."""
	with app.app_context():
		# Check if trains already exist
		if Train.query.count() > 0:
			print("✓ Trains already exist. Skipping...")
			return

		trains = [
			{
				"train_no": "IR-001",
				"name": "Express Alpha",
				"source": "Delhi",
				"destination": "Mumbai",
				"route": "Delhi -> Agra -> Indore -> Mumbai",
				"total_seats": 500,
				"classes_json": {"AC": 100, "Sleeper": 200, "General": 200},
				"fare_json": {"AC": 2500, "Sleeper": 1500, "General": 500},
				"schedule_json": {"departure": "08:00", "arrival": "20:00", "duration": "12h"}
			},
			{
				"train_no": "IR-002",
				"name": "Bangalore Express",
				"source": "Mumbai",
				"destination": "Bangalore",
				"route": "Mumbai -> Pune -> Belgaum -> Bangalore",
				"total_seats": 400,
				"classes_json": {"AC": 80, "Sleeper": 160, "General": 160},
				"fare_json": {"AC": 2000, "Sleeper": 1200, "General": 400},
				"schedule_json": {"departure": "10:00", "arrival": "22:00", "duration": "12h"}
			},
			{
				"train_no": "IR-003",
				"name": "Chennai Express",
				"source": "Delhi",
				"destination": "Chennai",
				"route": "Delhi -> Jaipur -> Hyderabad -> Chennai",
				"total_seats": 450,
				"classes_json": {"AC": 90, "Sleeper": 180, "General": 180},
				"fare_json": {"AC": 3000, "Sleeper": 1800, "General": 600},
				"schedule_json": {"departure": "06:00", "arrival": "18:00", "duration": "12h"}
			},
			{
				"train_no": "IR-004",
				"name": "Kolkata Express",
				"source": "Mumbai",
				"destination": "Kolkata",
				"route": "Mumbai -> Nagpur -> Raipur -> Kolkata",
				"total_seats": 380,
				"classes_json": {"AC": 76, "Sleeper": 152, "General": 152},
				"fare_json": {"AC": 2200, "Sleeper": 1400, "General": 450},
				"schedule_json": {"departure": "12:00", "arrival": "00:00", "duration": "12h"}
			},
			{
				"train_no": "IR-005",
				"name": "Goa Express",
				"source": "Bangalore",
				"destination": "Goa",
				"route": "Bangalore -> Hubli -> Goa",
				"total_seats": 350,
				"classes_json": {"AC": 70, "Sleeper": 140, "General": 140},
				"fare_json": {"AC": 1500, "Sleeper": 900, "General": 300},
				"schedule_json": {"departure": "14:00", "arrival": "23:00", "duration": "9h"}
			}
			,
			{
				"train_no": "IR-006",
				"name": "Northern Star",
				"source": "Delhi",
				"destination": "Lucknow",
				"route": "Delhi -> Ghaziabad -> Moradabad -> Lucknow",
				"total_seats": 420,
				"classes_json": {"AC": 90, "Sleeper": 180, "General": 150},
				"fare_json": {"AC": 1200, "Sleeper": 700, "General": 250},
				"schedule_json": {"departure": "09:00", "arrival": "15:00", "duration": "6h"}
			},
			{
				"train_no": "IR-007",
				"name": "Coastal Runner",
				"source": "Mumbai",
				"destination": "Goa",
				"route": "Mumbai -> Ratnagiri -> Goa",
				"total_seats": 360,
				"classes_json": {"AC": 60, "Sleeper": 150, "General": 150},
				"fare_json": {"AC": 1700, "Sleeper": 1000, "General": 350},
				"schedule_json": {"departure": "07:00", "arrival": "13:00", "duration": "6h"}
			},
			{
				"train_no": "IR-008",
				"name": "Eastern Express",
				"source": "Kolkata",
				"destination": "Patna",
				"route": "Kolkata -> Bardhaman -> Patna",
				"total_seats": 400,
				"classes_json": {"AC": 80, "Sleeper": 160, "General": 160},
				"fare_json": {"AC": 1400, "Sleeper": 850, "General": 300},
				"schedule_json": {"departure": "08:00", "arrival": "14:00", "duration": "6h"}
			},
			{
				"train_no": "IR-009",
				"name": "Southern Arrow",
				"source": "Bangalore",
				"destination": "Chennai",
				"route": "Bangalore -> Hosur -> Salem -> Chennai",
				"total_seats": 380,
				"classes_json": {"AC": 70, "Sleeper": 150, "General": 160},
				"fare_json": {"AC": 1100, "Sleeper": 700, "General": 250},
				"schedule_json": {"departure": "06:00", "arrival": "12:00", "duration": "6h"}
			},
			{
				"train_no": "IR-010",
				"name": "Capital Connector",
				"source": "Delhi",
				"destination": "Jaipur",
				"route": "Delhi -> Gurgaon -> Jaipur",
				"total_seats": 320,
				"classes_json": {"AC": 60, "Sleeper": 120, "General": 140},
				"fare_json": {"AC": 600, "Sleeper": 350, "General": 120},
				"schedule_json": {"departure": "05:00", "arrival": "09:00", "duration": "4h"}
			}
		]

		for t_data in trains:
			t = Train(**t_data)
			db.session.add(t)
		db.session.commit()
		print(f"✓ Added {len(trains)} sample trains")


def seed_seat_availability():
	"""Add seat availability for trains on future dates."""
	with app.app_context():
		if SeatAvailability.query.count() > 0:
			print("✓ Seat availability already exists. Skipping...")
			return

		trains = Train.query.all()
		base_date = date.today() + timedelta(days=1)

		for i in range(30):  # Next 30 days
			travel_date = base_date + timedelta(days=i)
			for train in trains:
				for cls, seats in (train.classes_json or {}).items():
					sa = SeatAvailability(
						train_id=train.id,
						travel_date=travel_date,
						cls=cls,
						seats_left=int(seats)
					)
					db.session.add(sa)
		db.session.commit()
		print(f"✓ Added seat availability for next 30 days")


def seed_test_users():
	"""Add demo test users."""
	with app.app_context():
		test_users = [
			{"username": "user1", "email": "user1@example.com", "password": "user123", "full_name": "John Passenger"},
			{"username": "user2", "email": "user2@example.com", "password": "user456", "full_name": "Jane Traveler"},
		]

		for u_data in test_users:
			existing = User.query.filter_by(username=u_data["username"]).first()
			if not existing:
				user = User(
					username=u_data["username"],
					email=u_data["email"],
					password_hash=generate_password_hash(u_data["password"]),
					full_name=u_data["full_name"],
					is_admin=False
				)
				db.session.add(user)
		db.session.commit()
		print(f"✓ Added {len(test_users)} test users")


if __name__ == "__main__":
	seed_trains()
	seed_seat_availability()
	seed_test_users()
	print("\n✓ Database seeded successfully!")
