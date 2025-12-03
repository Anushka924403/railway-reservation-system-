# utils.py
import random, string
from datetime import date, datetime, timedelta
from decimal import Decimal

def generate_pnr():
    # PNR = 10 char uppercase alnum
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

def calculate_refund(booking, cancel_date=None):
    # Simplified rules:
    # - If cancelled >72 hours before travel_date: 90% refund
    # - 24-72 hours: 50%
    # - <24 hours: 25%
    if cancel_date is None:
        cancel_date = datetime.utcnow().date()
    days_before = (booking.travel_date - cancel_date).days
    total = Decimal(booking.total_fare)
    if days_before > 3:
        pct = Decimal('0.90')
    elif days_before >= 1:
        pct = Decimal('0.50')
    else:
        pct = Decimal('0.25')
    refund = (total * pct).quantize(Decimal('0.01'))
    return refund

# Seat update function
def decrement_seats(db_session, train_id, travel_date, cls, count):
    from models import SeatAvailability, Train
    # fetch or create seat availability row
    sa = db_session.query(SeatAvailability).filter_by(train_id=train_id, travel_date=travel_date, cls=cls).first()
    if not sa:
        # initialize from train classes_json if present
        train = db_session.query(Train).filter_by(id=train_id).first()
        seats_total = 0
        try:
            seats_total = int(train.classes_json.get(cls, 0))
        except:
            seats_total = train.total_seats
        sa = SeatAvailability(train_id=train_id, travel_date=travel_date, cls=cls, seats_left=seats_total)
        db_session.add(sa)
        db_session.commit()
    if sa.seats_left < count:
        return False
    sa.seats_left -= count
    db_session.add(sa)
    db_session.commit()
    return True

def increment_seats(db_session, train_id, travel_date, cls, count):
    from models import SeatAvailability
    sa = db_session.query(SeatAvailability).filter_by(train_id=train_id, travel_date=travel_date, cls=cls).first()
    if not sa:
        return False
    sa.seats_left += count
    db_session.add(sa)
    db_session.commit()
    return True