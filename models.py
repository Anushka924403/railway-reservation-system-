# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(150))
    phone = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Train(db.Model):
    __tablename__ = "trains"
    id = db.Column(db.Integer, primary_key=True)
    train_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    route = db.Column(db.Text)  # JSON or CSV of stops+times
    total_seats = db.Column(db.Integer, default=0)
    classes_json = db.Column(db.JSON)
    fare_json = db.Column(db.JSON)
    schedule_json = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Booking(db.Model):
    __tablename__ = "bookings"
    id = db.Column(db.Integer, primary_key=True)
    pnr = db.Column(db.String(30), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    train_id = db.Column(db.Integer, db.ForeignKey("trains.id"), nullable=False)
    travel_date = db.Column(db.Date)
    cls = db.Column("class", db.String(10), nullable=False)
    seat_count = db.Column(db.Integer, nullable=False)
    fare_per_seat = db.Column(db.Numeric(10,2), nullable=False)
    total_fare = db.Column(db.Numeric(10,2), nullable=False)
    status = db.Column(db.Enum('CONFIRMED','CANCELLED','RAC','WL'), default='CONFIRMED')
    payment_status = db.Column(db.Enum('PAID','REFUNDED','PENDING'), default='PENDING')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class SeatAvailability(db.Model):
    __tablename__ = "seat_availability"
    id = db.Column(db.Integer, primary_key=True)
    train_id = db.Column(db.Integer, db.ForeignKey("trains.id"), nullable=False)
    travel_date = db.Column(db.Date, nullable=False)
    cls = db.Column("class", db.String(10), nullable=False)
    seats_left = db.Column(db.Integer, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (db.UniqueConstraint('train_id','travel_date','class', name='train_date_class'),)

class Payment(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    provider = db.Column(db.String(50))
    provider_payment_id = db.Column(db.String(100))
    amount = db.Column(db.Numeric(10,2), nullable=False)
    currency = db.Column(db.String(10), default='INR')
    status = db.Column(db.Enum('SUCCESS','FAILED','REFUNDED','PENDING'), default='PENDING')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FoodOrder(db.Model):
    __tablename__ = "food_orders"
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    items = db.Column(db.Text, nullable=False)  # JSON string of items
    amount = db.Column(db.Numeric(10,2), nullable=False)
    status = db.Column(db.Enum('PLACED','PREPARING','ONBOARD','DELIVERED','CANCELLED'), default='PLACED')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)