import sys
import json
from warcio.archiveiterator import ArchiveIterator

items = []

with open(sys.argv[1], 'rb') as stream:
    for record in ArchiveIterator(stream):
        if record.rec_type != 'response':
            continue
        if record.rec_headers.get_header('WARC-Target-URI') != 'https://www.amazon.co.jp/hz/mycd/ajax':
            continue
        data = json.loads(record.content_stream().read())
        if not 'OwnershipData' in data:
            continue
        for item in data['OwnershipData']['items']:
            items.append(item)

def get_sort_key(item):
    return item['sortableTitle']
items.sort(key=get_sort_key)

for item in items:
    print(json.dumps(item))
