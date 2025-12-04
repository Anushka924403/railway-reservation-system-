
# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from config import Config
from models import db, User, Train, Booking, SeatAvailability, Payment, FoodOrder
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from utils import generate_pnr, calculate_refund, decrement_seats, increment_seats
import uuid
import io
import json
from flask import jsonify
import random

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/home')
@login_required
def home():
	trains = Train.query.all()
	return render_template('home.html', trains=trains)


# ----------------- Auth -----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		username = request.form['username']
		email = request.form['email']
		pw = request.form['password']
		if User.query.filter((User.username == username) | (User.email == email)).first():
			return "User exists", 400
		u = User(username=username, email=email, password_hash=generate_password_hash(pw), full_name=request.form.get('full_name'))
		db.session.add(u)
		db.session.commit()
		return redirect(url_for('login'))
	return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		uname = request.form['username']
		pw = request.form['password']
		u = User.query.filter((User.username == uname) | (User.email == uname)).first()
		if not u or not check_password_hash(u.password_hash, pw):
			return "Invalid credentials", 401
		login_user(u)
		if u.is_admin:
			return redirect(url_for('home'))
		return redirect(url_for('home'))
	return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
	logout_user()
	return redirect(url_for('index'))


# ----------------- Admin -----------------
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
	if not current_user.is_admin:
		return "Forbidden", 403
	# summary stats
	total_trains = Train.query.count()
	total_bookings = Booking.query.count()
	total_users = User.query.count()
	return render_template('admin_dashboard.html', total_trains=total_trains, total_bookings=total_bookings, total_users=total_users)


# Add train
@app.route('/admin/train/add', methods=['POST'])
@login_required
def admin_add_train():
	if not current_user.is_admin:
		return "Forbidden", 403
	data = request.get_json()
	t = Train(
		train_no=data['train_no'],
		name=data['name'],
		source=data['source'],
		destination=data['destination'],
		route=data.get('route', ''),
		total_seats=int(data.get('total_seats', 0)),
		classes_json=data.get('classes_json', {}),
		fare_json=data.get('fare_json', {}),
		schedule_json=data.get('schedule_json', {})
	)
	db.session.add(t)
	db.session.commit()
	return jsonify({"status": "ok", "train_id": t.id})


# Update train, delete train etc. (similar patterns)
@app.route('/admin/train/<int:train_id>/update', methods=['POST'])
@login_required
def admin_update_train(train_id):
	if not current_user.is_admin:
		return "Forbidden", 403
	t = Train.query.get_or_404(train_id)
	data = request.get_json()
	for k in ['name', 'source', 'destination', 'route', 'total_seats', 'classes_json', 'fare_json', 'schedule_json']:
		if k in data:
			setattr(t, k, data[k])
	db.session.commit()
	return jsonify({"status": "ok"})


@app.route('/admin/train/<int:train_id>/delete', methods=['POST'])
@login_required
def admin_delete_train(train_id):
	if not current_user.is_admin:
		return "Forbidden", 403
	t = Train.query.get_or_404(train_id)
	db.session.delete(t)
	db.session.commit()
	return jsonify({"status": "deleted"})


# ----------------- Public: Search / View -----------------
@app.route('/trains')
def view_trains():
	trains = Train.query.all()
	trains_out = []
	for t in trains:
		trains_out.append({
			"id": t.id,
			"train_no": t.train_no,
			"name": t.name,
			"source": t.source,
			"destination": t.destination,
			"classes": t.classes_json or {}
		})
	return jsonify(trains_out)


@app.route('/search', methods=['GET'])
def search_train():
	source = request.args.get('source')
	dest = request.args.get('dest')
	date_str = request.args.get('date')  # YYYY-MM-DD
	q = Train.query
	if source:
		q = q.filter(Train.source.ilike(f"%{source}%"))
	if dest:
		q = q.filter(Train.destination.ilike(f"%{dest}%"))
	trains = q.all()
	results = []
	for t in trains:
		results.append({
			"id": t.id, "train_no": t.train_no, "name": t.name,
			"source": t.source, "destination": t.destination, "classes": t.classes_json
		})
	return render_template('search_results.html', results=results, date=date_str)


# ----------------- Static pages: Contact / Help / About / Meal / History -----------------
@app.route('/contact', methods=['GET', 'POST'])
def contact_page():
	success = False
	if request.method == 'POST':
		# In a real app we'd send/store the message. For demo, just acknowledge.
		name = request.form.get('name')
		mobile = request.form.get('mobile')
		message = request.form.get('message')
		# TODO: store or email
		success = True
	return render_template('contact.html', success=success)


@app.route('/help')
def help_page():
	return render_template('help.html')


@app.route('/about')
def about_page():
	return render_template('about.html')


@app.route('/meal')
def meal_page():
	return render_template('meal.html')


@app.route('/history')
@login_required
def history_page():
	# Show user's bookings
	bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
	return render_template('history.html', bookings=bookings)


@app.route('/train/<int:train_id>')
def train_details(train_id):
	t = Train.query.get_or_404(train_id)
	return jsonify({
		"id": t.id,
		"train_no": t.train_no,
		"name": t.name,
		"source": t.source,
		"destination": t.destination,
		"route": t.route,
		"classes": t.classes_json,
		"fare": t.fare_json
	})


@app.route('/assistant', methods=['POST'])
def assistant():
	"""Simple rule-based assistant placeholder. Returns JSON reply."""
	data = request.get_json() or {}
	q = data.get('query', '').strip()
	if not q:
		return jsonify({'reply': "Hi — I can help estimate delays, predict platforms, help with bookings and onboard food. Try: 'estimate delay for IR-001 on 2025-12-05'"})

	ql = q.lower()
	# Try to parse delay request: look for train number and date
	import re
	m = re.search(r"(ir[- ]?\d{1,3})", ql)
	d = None
	md = re.search(r"(\d{4}-\d{2}-\d{2})", q)
	if md:
		d = md.group(1)
	train_no = m.group(1).replace(' ', '').upper() if m else None

	if 'delay' in ql or 'late' in ql:
		if train_no and d:
			# find train id from train_no
			t = Train.query.filter(Train.train_no.ilike(f"%{train_no}%")).first()
			if t:
				# deterministic pseudo-estimate
				est = abs(hash(f"{t.id}:{d}")) % 60
				return jsonify({'reply': f"Estimated delay for {t.train_no} on {d} is around {est} minutes."})
			else:
				return jsonify({'reply': f"I couldn't find train {train_no}. Please provide a valid train number."})
		return jsonify({'reply': "To estimate delay, include train number and date (YYYY-MM-DD). Example: 'estimate delay for IR-001 on 2025-12-05'"})

	if 'platform' in ql:
		if train_no:
			t = Train.query.filter(Train.train_no.ilike(f"%{train_no}%")).first()
			if t:
				p = (abs(hash(str(t.id))) % 12) + 1
				return jsonify({'reply': f"Predicted platform for {t.train_no} is platform {p} (approx)."})
			else:
				return jsonify({'reply': f"I couldn't find train {train_no}."})
		return jsonify({'reply': "To predict platform, include the train number. Example: 'predict platform for IR-001'"})

	if 'food' in ql or 'meal' in ql or 'order' in ql:
		return jsonify({'reply': "To order food, open the 'Order Food' panel on your booking or provide your PNR. I can place orders and show order history."})

	# fallback small chat responses
	if 'hello' in ql or 'hi' in ql:
		return jsonify({'reply': "Hello! I can estimate delays, predict platforms, help you book trains and order food onboard."})

	return jsonify({'reply': "Sorry, I didn't understand that. Try asking about delays, platforms, bookings or food orders (include train number/date where relevant)."})


@app.route('/predict_delay')
def predict_delay():
	"""Return a simple estimated delay (minutes) for a train on a date.
	This is a placeholder using deterministic pseudo-random based on train id + date.
	"""
	train_id = request.args.get('train_id')
	date_str = request.args.get('date')
	if not train_id or not date_str:
		return jsonify({'error': 'train_id and date required'}), 400
	# deterministic pseudo-random
	seed = hash(f"{train_id}:{date_str}")
	rng = abs(seed) % 60  # up to 59 minutes
	# simple bias: peak hours more delay (example)
	est = rng
	return jsonify({'train_id': train_id, 'date': date_str, 'estimated_delay_minutes': int(est)})


@app.route('/predict_platform')
def predict_platform():
	train_id = request.args.get('train_id')
	if not train_id:
		return jsonify({'error': 'train_id required'}), 400
	# Map to platform 1-12 deterministically
	p = (abs(hash(train_id)) % 12) + 1
	return jsonify({'train_id': train_id, 'predicted_platform': p})


@app.route('/menu')
def menu():
	# static menu with categories
	menu = {
		"categories": [
			{"id": "veg", "name": "Vegetarian", "items": [{"id": "v1", "name": "Paneer Wrap", "price": 200}, {"id": "v2", "name": "Veg Biryani", "price": 180}, {"id": "v3", "name": "Salad", "price": 120}]},
			{"id": "nonveg", "name": "Non-Veg", "items": [{"id": "n1", "name": "Chicken Biryani", "price": 250}, {"id": "n2", "name": "Grilled Chicken", "price": 300}]},
			{"id": "snacks", "name": "Snacks & Drinks", "items": [{"id": "s1", "name": "Samosa", "price": 40}, {"id": "s2", "name": "Tea", "price": 30}, {"id": "s3", "name": "Cold Drink", "price": 60}]}
		]
	}
	return jsonify(menu)


@app.route('/order_history')
@login_required
def order_history():
	orders = FoodOrder.query.filter_by(user_id=current_user.id).order_by(FoodOrder.created_at.desc()).all()
	out = []
	for o in orders:
		out.append({
			'order_id': o.id,
			'booking_id': o.booking_id,
			'items': json.loads(o.items),
			'amount': float(o.amount),
			'status': o.status,
			'created_at': o.created_at.isoformat()
		})
	return jsonify({'orders': out})


@app.route('/order_food', methods=['POST'])
@login_required
def order_food():
	data = request.get_json() or {}
	items = data.get('items')
	amount = float(data.get('amount', 0))
	booking_pnr = data.get('pnr')
	booking = None
	if booking_pnr:
		booking = Booking.query.filter_by(pnr=booking_pnr).first()
	fo = None
	if not items or amount <= 0:
		return jsonify({'error': 'items and amount required'}), 400
	fo = None
	if booking:
		fo = FoodOrder(booking_id=booking.id, user_id=current_user.id, items=json.dumps(items), amount=amount)
	else:
		fo = FoodOrder(booking_id=None, user_id=current_user.id, items=json.dumps(items), amount=amount)
	db.session.add(fo)
	db.session.commit()
	return jsonify({'status': 'placed', 'order_id': fo.id})


# Check seat availability
@app.route('/availability/<int:train_id>')
def check_availability(train_id):
	travel_date = request.args.get('date')
	cls = request.args.get('class')
	if not travel_date or not cls:
		return jsonify({"error": "date and class required"}), 400
	sa = SeatAvailability.query.filter_by(train_id=train_id, travel_date=travel_date, cls=cls).first()
	seats_left = sa.seats_left if sa else None
	return jsonify({"train_id": train_id, "date": travel_date, "class": cls, "seats_left": seats_left})


# ----------------- Booking -----------------
@app.route('/book/<int:train_id>', methods=['GET', 'POST'])
@login_required
def book_ticket(train_id):
	t = Train.query.get_or_404(train_id)
	if request.method == 'POST':
		journey_date = datetime.strptime(request.form['journey_date'], '%Y-%m-%d').date()
		cls = request.form['class']
		seat_count = int(request.form['seats'])
		fare_per = float(t.fare_json.get(cls, 0))
		total = fare_per * seat_count
		# check seats
		success = decrement_seats(db.session, train_id, journey_date, cls, seat_count)
		if not success:
			return "Not enough seats", 400
		pnr = generate_pnr()
		booking = Booking(pnr=pnr, user_id=current_user.id, train_id=train_id,
						  travel_date=journey_date, cls=cls, seat_count=seat_count,
						  fare_per_seat=fare_per, total_fare=total, status='CONFIRMED', payment_status='PENDING')
		db.session.add(booking)
		db.session.commit()
		# Redirect to payment page
		return redirect(url_for('payment_page', pnr=pnr))
	# GET -> show booking form
	return render_template('book.html', train=t)


@app.route('/payment/<pnr>', methods=['GET', 'POST'])
@login_required
def payment_page(pnr):
	booking = Booking.query.filter_by(pnr=pnr).first_or_404()
	if booking.user_id != current_user.id and not current_user.is_admin:
		return "Forbidden", 403
	if booking.payment_status != 'PENDING':
		return redirect(url_for('booking_confirmation', pnr=pnr))
	train = Train.query.get(booking.train_id)
	
	if request.method == 'POST':
		# Process payment
		payment_method = request.form.get('payment_method')
		# Simulate payment processing - in production connect to actual payment gateway
		# For demo: auto-approve
		booking.payment_status = 'PAID'
		db.session.commit()
		
		# Create payment record
		pay = Payment(
			booking_id=booking.id,
			provider=payment_method or 'CARD',
			provider_payment_id=str(uuid.uuid4()),
			amount=booking.total_fare,
			status='SUCCESS'
		)
		db.session.add(pay)
		db.session.commit()
		
		return redirect(url_for('booking_confirmation', pnr=pnr))
	
	return render_template('payment.html', booking=booking, train=train)


@app.route('/booking/<pnr>')
@login_required
def booking_confirmation(pnr):
	booking = Booking.query.filter_by(pnr=pnr).first_or_404()
	if booking.user_id != current_user.id and not current_user.is_admin:
		return "Forbidden", 403
	train = Train.query.get(booking.train_id)
	return render_template('ticket.html', booking=booking, train=train)


# Cancel booking
@app.route('/cancel/<pnr>', methods=['POST'])
@login_required
def cancel_booking(pnr):
	booking = Booking.query.filter_by(pnr=pnr).first_or_404()
	if booking.user_id != current_user.id and not current_user.is_admin:
		return "Forbidden", 403
	if booking.status == 'CANCELLED':
		return "Already cancelled", 400
	refund = calculate_refund(booking, cancel_date=datetime.utcnow().date())
	# Mark booking cancelled and payment refunded (demo)
	booking.status = 'CANCELLED'
	booking.payment_status = 'REFUNDED'
	db.session.commit()
	# increment seats back
	increment_seats(db.session, booking.train_id, booking.travel_date, booking.cls, booking.seat_count)
	# update payment record (simplified)
	payment = Payment.query.filter_by(booking_id=booking.id).first()
	if payment:
		payment.status = 'REFUNDED'
		db.session.commit()
	return jsonify({"status": "cancelled", "refund_amount": str(refund)})


# Reports (admin)
@app.route('/admin/reports/daily')
@login_required
def daily_report():
	if not current_user.is_admin:
		return "Forbidden", 403
	# sample: bookings per day
	from sqlalchemy import func
	results = db.session.query(func.date(Booking.created_at).label('d'), func.count(Booking.id), func.sum(Booking.total_fare)).group_by('d').all()
	out = [{"date": str(r[0]), "bookings": int(r[1]), "revenue": float(r[2] or 0)} for r in results]
	return jsonify(out)


# Download ticket as simple HTML -> downloadable file
@app.route('/download_ticket/<pnr>')
@login_required
def download_ticket(pnr):
	booking = Booking.query.filter_by(pnr=pnr).first_or_404()
	if booking.user_id != current_user.id and not current_user.is_admin:
		return "Forbidden", 403
	# For demo: return an HTML document as attachment
	train = Train.query.get(booking.train_id)
	html = render_template('ticket.html', booking=booking, train=train)
	return (html, 200, {'Content-Type': 'text/html', 'Content-Disposition': f'attachment;filename=ticket_{pnr}.html'})


if __name__ == '__main__':
	app.run(debug=True)
