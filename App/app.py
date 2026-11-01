#!/usr/bin/env python3
"""Local lunch planner. Python standard library only; no cloud services."""
import datetime
import json
import re
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from zipfile import ZipFile
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / 'Data'
NS = {'s': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

def rows(path):
    """Read the first worksheet, supporting inline, shared and plain strings."""
    with ZipFile(path) as z:
        shared = []
        if 'xl/sharedStrings.xml' in z.namelist():
            shared = [''.join(n.itertext()) for n in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        result = []
        for row in ET.fromstring(z.read('xl/worksheets/sheet1.xml')).findall('.//s:sheetData/s:row', NS):
            values = {}
            for cell in row.findall('s:c', NS):
                col = 0
                for c in re.match(r'[A-Z]+', cell.attrib['r']).group():
                    col = col * 26 + ord(c) - 64
                kind = cell.get('t')
                v = cell.find('s:v', NS)
                if kind == 'inlineStr':
                    value = ''.join(n.text or '' for n in cell.findall('.//s:t', NS))
                elif v is None:
                    value = None
                elif kind == 's':
                    value = shared[int(v.text)]
                elif kind in ('str', 'e', 'b'):
                    value = v.text
                else:
                    value = float(v.text)
                values[col - 1] = value
            if values:
                result.append([values.get(i) for i in range(max(values) + 1)])
        return result

def minutes(value):
    if not isinstance(value, (int, float)) or not 0 <= value < 1440:
        raise ValueError('Timings must be numbers from 0 to less than 1440 minutes.')
    return value

def load_data():
    travel = rows(DATA / 'travel_times_sample.xlsx')
    waits = rows(DATA / 'restaurant_wait_times_sample.xlsx')
    if not travel or travel[0] != ['Start location', 'Final location', 'walk distance (min)']:
        raise ValueError('Travel file must have Start location, Final location, and walk distance (min) headers.')
    bands = []
    for header in waits[0][1:]:
        match = re.fullmatch(r'(\d{2}):(\d{2})[–-](\d{2}):(\d{2})', str(header))
        if not match:
            raise ValueError('Waiting-time headers must use HH:MM–HH:MM.')
        h1, m1, h2, m2 = map(int, match.groups())
        lo, hi = h1 * 60 + m1, h2 * 60 + m2
        if m1 > 59 or m2 > 59 or not 0 <= lo < hi <= 1440 or (bands and lo < bands[-1][1]):
            raise ValueError('Time bands must be ordered and must not overlap.')
        bands.append((lo, hi, header))
    routes, locations, restaurants = {}, set(), {}
    for row in travel[1:]:
        if len(row) != 3 or not all(isinstance(x, str) and x.strip() for x in row[:2]):
            raise ValueError('Each travel row needs two location names and a time.')
        a, b, value = row
        key = frozenset((a, b))
        if key in routes:
            raise ValueError('Duplicate travel pair: %s / %s' % (a, b))
        routes[key] = None if value is None else minutes(value)
        locations.add(a)
    for row in waits[1:]:
        name = row[0]
        if not isinstance(name, str) or not name.strip() or name in restaurants:
            raise ValueError('Restaurant names must be present and unique.')
        vals = row[1:] + [None] * (len(bands) - len(row[1:]))
        if len(vals) != len(bands):
            raise ValueError('Unexpected restaurant time columns.')
        restaurants[name] = [None if v is None else minutes(v) for v in vals]
    if not locations or not restaurants or not bands:
        raise ValueError('The files need at least one campus location, restaurant and time band.')
    return routes, sorted(locations), restaurants, bands

def rank(start, end, departure, data):
    routes, locations, restaurants, bands = data
    if start not in locations or end not in locations:
        raise ValueError('Select valid start and destination locations.')
    if not re.fullmatch(r'(?:[01]\d|2[0-3]):[0-5]\d', departure):
        raise ValueError('Enter departure time as HH:MM.')
    h, m = map(int, departure.split(':'))
    results, unavailable = [], []
    for name, waits in restaurants.items():
        outward = routes.get(frozenset((start, name)))
        onward = routes.get(frozenset((end, name)))
        if outward is None or onward is None:
            unavailable.append({'name': name, 'reason': 'Walking time unavailable'})
            continue
        arrival = h * 60 + m + outward
        band = next((i for i, (lo, hi, _) in enumerate(bands) if lo <= arrival < hi), None)
        if band is None or waits[band] is None:
            unavailable.append({'name': name, 'reason': 'No waiting estimate at restaurant arrival time'})
            continue
        wait = waits[band]
        results.append({'name': name, 'outbound': outward, 'wait': wait, 'onward': onward,
                        'total': outward + wait + onward, 'band': bands[band][2]})
    results.sort(key=lambda r: (r['total'], r['name'].casefold()))
    for i, result in enumerate(results):
        result['rank'] = results[i-1]['rank'] if i and results[i-1]['total'] == result['total'] else i + 1
    return {'results': results, 'unavailable': unavailable}

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        url = urlparse(self.path)
        try:
            if url.path == '/':
                content, kind = (HERE / 'index.html').read_bytes(), 'text/html; charset=utf-8'
            elif url.path == '/api/locations':
                content = json.dumps({'locations': load_data()[1]}).encode()
                kind = 'application/json'
            elif url.path == '/api/rank':
                q = parse_qs(url.query)
                content = json.dumps(rank(q.get('start', [''])[0], q.get('end', [''])[0], q.get('time', [''])[0], load_data())).encode()
                kind = 'application/json'
            else:
                self.send_error(404)
                return
            self.send_response(200)
        except Exception as exc:
            content, kind = json.dumps({'error': str(exc)}).encode(), 'application/json'
            self.send_response(400)
        self.send_header('Content-Type', kind)
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(content)

if __name__ == '__main__':
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    address = 'http://127.0.0.1:%d' % server.server_port
    print('Lunch planner: ' + address + '\nKeep this window open. Press Control+C to stop.', flush=True)
    threading.Timer(0.5, lambda: webbrowser.open(address)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
