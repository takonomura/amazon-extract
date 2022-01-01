import sys
import json
import re
from warcio.archiveiterator import ArchiveIterator
from bs4 import BeautifulSoup

def find_date(row):
    section = row.find(class_='transaction-date')
    tag = section.find(attrs={'data-date-timestamp': True})
    return int(tag['data-date-timestamp'])

def find_description(row):
    wrapper = row.find(class_='transaction-description-main-content')
    tag = wrapper.find(class_='a-truncate-full')
    return tag.text.strip()

def find_order_url(row):
    tag = row.find(href=re.compile('^/gp/your-account/order-details/.+'))
    if tag:
        return "https://www.amazon.co.jp" + re.sub('ref=[a-z0-9_]+', '', tag['href'])
    tag = row.find(href=re.compile('^/gp/digital/your-account/order-summary.html/.+'))
    if tag:
        return "https://www.amazon.co.jp" + re.sub('ref=[a-z0-9_]+', '', tag['href'])
    return None

def find_type(row):
    return row.find(class_='transaction-badge')['data-badge-type']

def find_points(row):
    section = row.find(class_='transaction-points')
    tag = section.find(class_='a-size-large')
    return int(tag.text.strip().replace('+', '').replace(',', ''))

def is_point_confirmed(row):
    return not '獲得予定' in row.find(class_='transaction-points').text

def parse_tab_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    items = []
    for row in soup.find_all(class_='transaction-row'):
        items.append({
            'date': find_date(row),
            'description': find_description(row),
            'order_url': find_order_url(row),
            'type': find_type(row),
            'points': find_points(row),
            'confirmed': is_point_confirmed(row),
        })
    return items

items = []
with open(sys.argv[1], 'rb') as stream:
    for record in ArchiveIterator(stream):
        if record.rec_type != 'response':
            continue
        if not record.rec_headers.get_header('WARC-Target-URI').startswith('https://www.amazon.co.jp/mypoints/transactions/ref='):
            continue
        data = json.loads(record.content_stream().read())
        tab_items = parse_tab_html(data['tabHtml'])
        items.extend(tab_items)

def get_date(item):
    return item['date']
items.sort(key=get_date)

for item in items:
    print(json.dumps(item))
