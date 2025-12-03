
# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify, send_file
from config import Config
from models import db, User, Train, Booking, SeatAvailability, Payment
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from utils import generate_pnr, calculate_refund, decrement_seats, increment_seats
import uuid
import io

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

# ----------------- Auth -----------------
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        pw = request.form['password']
        if User.query.filter((User.username==username)|(User.email==email)).first():
            return "User exists", 400
        u = User(username=username, email=email, password_hash=generate_password_hash(pw), full_name=request.form.get('full_name'))
        db.session.add(u); db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pw = request.form['password']
        u = User.query.filter((User.username==uname)|(User.email==uname)).first()
        if not u or not check_password_hash(u.password_hash, pw):
            return "Invalid credentials", 401
        login_user(u)
        if u.is_admin:
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('index'))
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
    db.session.add(t); db.session.commit()
    return jsonify({"status":"ok","train_id":t.id})

# Update train, delete train etc. (similar patterns)
@app.route('/admin/train/<int:train_id>/update', methods=['POST'])
@login_required
def admin_update_train(train_id):
    if not current_user.is_admin:
        return "Forbidden", 403
    t = Train.query.get_or_404(train_id)
    data = request.get_json()
    for k in ['name','source','destination','route','total_seats','classes_json','fare_json','schedule_json']:
        if k in data:
            setattr(t, k, data[k])
    db.session.commit()
    return jsonify({"status":"ok"})

@app.route('/admin/train/<int:train_id>/delete', methods=['POST'])
@login_required
def admin_delete_train(train_id):
    if not current_user.is_admin:
        return "Forbidden", 403
    t = Train.query.get_or_404(train_id)
    db.session.delete(t)
    db.session.commit()
    retur

Anushka Tiwari, [02-12-2025 17:45]
n jsonify({"status":"deleted"})

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
    date_str = request.args.get('date')  # YYYY-MM-DD
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

# Check seat availability
@app.route('/availability/<int:train_id>')
def check_availability(train_id):
    travel_date = request.args.get('date')
    cls = request.args.get('class')
    if not travel_date or not cls:
        return jsonify({"error":"date and class required"}), 400
    sa = SeatAvailability.query.filter_by(train_id=train_id, travel_date=travel_date, cls=cls).first()
    seats_left = sa.seats_left if sa else None
    return jsonify({"train_id":train_id,"date":travel_date,"class":cls,"seats_left":seats_left})

# ----------------- Booking -----------------
@app.route('/book/<int:train_id>', methods=['GET','POST'])
@login_required
def book_ticket(train_id):
    t = Train.query.get_or_404(train_id)
    if request.method == 'POST':
        travel_date = datetime.strptime(request.form['travel_date'],'%Y-%m-%d').date()
        cls = request.form['class']
        seat_count = int(request.form['seat_count'])
        fare_per = float(t.fare_json.get(cls, 0))
        total = fare_per * seat_count
        # check seats
        success = decrement_seats(db.session, train_id, travel_date, cls, seat_count)
        if not success:
            return "Not enough seats", 400
        pnr = generate_pnr()
        booking = Booking(pnr=pnr, user_id=current_user.id, train_id=train_id,
                          travel_date=travel_date, cls=cls, seat_count=seat_count,
                          fare_per_seat=fare_per, total_fare=total, status='CONFIRMED', payment_status='PENDING')
        db.session.add(booking)
        db.session.commit()
        # Here you'd redirect to a payment gateway; for now we mark PAID for demonstration
        booking.payment_status = 'PAID'
        db.session.commit()
        # Create payment record
        pay = Payment(booking_id=booking.id, provider='TEST', provider_payment_id=str(uuid.uuid4()), amount=total, status='SUCCESS')
        db.session.add(pay); db.session.commit()
        return redirect(url_for('booking_confirmation', pnr=pnr))
    # GET -> show booking form
    return render_template('book.html', train=t)

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
    booking = Booking.q

Anushka Tiwari, [02-12-2025 17:45]
uery.filter_by(pnr=pnr).first_or_404()
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
        payment.status = 'REFUNDED'; db.session.commit()
    return jsonify({"status":"cancelled","refund_amount":str(refund)})

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
