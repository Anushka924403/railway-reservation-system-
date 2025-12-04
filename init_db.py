#!/usr/bin/env python3
"""Initialize the SQLite database and create a default admin user.

Run: python init_db.py
"""
from app import app
from models import db, User
from werkzeug.security import generate_password_hash


def init_db():
    with app.app_context():
        print('Creating database tables...')
        db.create_all()
        # Create default admin user if not present
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print('Admin user already exists (username: admin)')
        else:
            pw = 'admin123'
            admin = User(username='admin', email='admin@example.com', password_hash=generate_password_hash(pw), full_name='Administrator', is_admin=True)
            db.session.add(admin)
            db.session.commit()
            print('Created admin user: username=admin password=%s' % pw)


if __name__ == '__main__':
    init_db()
