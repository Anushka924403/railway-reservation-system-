#!/usr/bin/env python3
import requests, sys, json
from datetime import date, timedelta

BASE = 'http://127.0.0.1:5000'
# credentials from seed / conversation
USERNAME='user1'
PASSWORD='user123'

s = requests.Session()
print('Logging in...')
resp = s.post(f'{BASE}/login', data={'username': USERNAME, 'password': PASSWORD}, allow_redirects=True)
if resp.status_code not in (200, 302):
    print('Login failed:', resp.status_code)
    print(resp.text[:400])
    sys.exit(1)
print('Logged in successfully (status)', resp.status_code)

print('Fetching trains list...')
resp = s.get(f'{BASE}/trains')
trains = resp.json()
if not trains:
    print('No trains found')
    sys.exit(1)
train = trains[0]
train_id = train['id']
print('Selected train id=', train_id, 'name=', train.get('name'))

print('Fetching train details...')
resp = s.get(f'{BASE}/train/{train_id}')
info = resp.json()
fare = info.get('fare') or {}
classes = list(fare.keys())
if not classes:
    # fallback to classes_json
    classes = list(info.get('classes', {}).keys())
if not classes:
    print('No classes available on train')
    sys.exit(1)
selected_class = classes[0]
print('Selected class:', selected_class, 'fare:', fare.get(selected_class))

# choose tomorrow as journey
journey = (date.today() + timedelta(days=1)).isoformat()
print('Journey date:', journey)

print('Submitting booking...')
book_resp = s.post(f'{BASE}/book/{train_id}', data={'journey_date': journey, 'class': selected_class, 'seats': '1'}, allow_redirects=False)
if book_resp.status_code not in (302, 303):
    print('Booking POST failed', book_resp.status_code)
    print(book_resp.text[:800])
    sys.exit(1)
# follow redirect to payment page
loc = book_resp.headers.get('Location')
print('Booking created, redirect location:', loc)
if not loc:
    print('No redirect location; cannot proceed')
    sys.exit(1)

# GET payment page (follow)
pay_page = s.get(BASE + loc)
if pay_page.status_code != 200:
    print('Failed to load payment page', pay_page.status_code)
    sys.exit(1)
# find PNR in the page or derive from loc
pnr = loc.rstrip('/').split('/')[-1]
print('PNR for booking:', pnr)

print('Posting payment...')
pay_post = s.post(f'{BASE}/payment/{pnr}', data={'payment_method':'CARD'}, allow_redirects=False)
if pay_post.status_code not in (302,303):
    print('Payment POST failed', pay_post.status_code)
    print(pay_post.text[:800])
    sys.exit(1)
print('Payment processed, redirect to:', pay_post.headers.get('Location'))

# follow to ticket
ticket_loc = pay_post.headers.get('Location')
resp = s.get(BASE + ticket_loc)
if resp.status_code != 200:
    print('Failed to load ticket page', resp.status_code)
    sys.exit(1)

html = resp.text
# save ticket HTML
import os
os.makedirs('tickets', exist_ok=True)
path = os.path.join('tickets', f'ticket_{pnr}.html')
with open(path, 'w', encoding='utf-8') as f:
    f.write(html)
print('Saved ticket to', path)
print('You can open the dev server at: http://127.0.0.1:5000/booking/{}'.format(pnr))
print('Test completed successfully')
