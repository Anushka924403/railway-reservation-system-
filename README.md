# Railway Reservation - Local Run Guide

Quick steps to get this project running locally (uses SQLite by default):

1. Create a Python virtual environment and activate it:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Initialize the database (creates `railway.db` and a default admin user):

```bash
python init_db.py
```

Default admin credentials: `username=admin`, `password=admin123` (change after first login).

4. Run the app:

```bash
python app.py
```

5. Browse to `http://127.0.0.1:5000/`.

Notes:
- `config.py` defaults to `sqlite:///railway.db` for local development. To use another DB, set the `DATABASE_URI` env var.
- The templates provided are minimal for local testing.
# railway-reservation-system-
its my minor project
