#!/usr/bin/env python3
import requests, sys, json, os
from datetime import date, timedelta

BASE = 'http://127.0.0.1:5000'
USERNAME='user1'
PASSWORD='user123'

s = requests.Session()
print('Logging in...')
resp = s.post(f'{BASE}/login', data={'username': USERNAME, 'password': PASSWORD}, allow_redirects=True)
if resp.status_code not in (200,302):
    print('Login failed:', resp.status_code)
    print(resp.text[:400])
    sys.exit(1)
print('Logged in')

resp = s.get(f'{BASE}/trains')
trains = resp.json()
if not trains:
    print('No trains found')
    sys.exit(1)

os.makedirs('tickets', exist_ok=True)
orders_summary = []

for t in trains[:10]:
    tid = t['id']
    print('\nProcessing train', t.get('train_no'), t.get('name'))
    # get full details
    info = s.get(f'{BASE}/train/{tid}').json()
    fare = info.get('fare') or {}
    classes = list(fare.keys())
    if not classes:
        classes = list(info.get('classes', {}).keys())
    if not classes:
        print(' no classes for train')
        continue
    cls = classes[0]
    journey = (date.today() + timedelta(days=1)).isoformat()
    # book
    print(' booking class', cls, 'date', journey)
    book = s.post(f'{BASE}/book/{tid}', data={'journey_date': journey, 'class': cls, 'seats': '1'}, allow_redirects=False)
    if book.status_code not in (302,303):
        print(' booking failed', book.status_code, book.text[:300])
        continue
    loc = book.headers.get('Location')
    # follow payment page
    pnr = loc.rstrip('/').split('/')[-1]
    pay_page = s.get(BASE + loc)
    # pay
    pay_post = s.post(f'{BASE}/payment/{pnr}', data={'payment_method': 'CARD'}, allow_redirects=False)
    if pay_post.status_code not in (302,303):
        print(' payment failed', pay_post.status_code)
        continue
    ticket_loc = pay_post.headers.get('Location')
    ticket = s.get(BASE + ticket_loc)
    ticket_path = os.path.join('tickets', f'ticket_{pnr}.html')
    with open(ticket_path, 'w', encoding='utf-8') as f:
        f.write(ticket.text)
    print(' saved ticket', ticket_path)
    # menu and order
    menu = s.get(f'{BASE}/menu').json()
    first_item = menu['categories'][0]['items'][0]
    order_payload = {'items': [{'id': first_item['id'], 'qty': 1}], 'amount': first_item['price'], 'pnr': pnr}
    order = s.post(f'{BASE}/order_food', json=order_payload).json()
    print(' placed order', order)
    orders_summary.append({'pnr': pnr, 'order': order})
    # order history
    hist = s.get(f'{BASE}/order_history').json()
    print(' order history entries:', len(hist.get('orders', [])))

print('\nDone. Tickets saved in ./tickets. Summary:')
print(json.dumps(orders_summary, indent=2))
print('\nOpen the app at http://127.0.0.1:5000')
