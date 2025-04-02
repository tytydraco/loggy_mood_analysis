import os
import base64
import gzip
import json
import datetime
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
import numpy as np

CWD = os.path.dirname(os.path.realpath(__file__))
INPUT_FILE = f'{CWD}/input.txt'
JSON_FILE = f'{CWD}/list.json'
AVERAGES_FILE = f'{CWD}/averages.json'

if not os.path.exists(INPUT_FILE):
    print('input.txt does not exist.')
    exit(1)

with open(INPUT_FILE, 'r') as f:
    contents = f.read()

contents_base64_decoded = base64.b64decode(contents)
contents_gzip_deflated = gzip.decompress(contents_base64_decoded)
list_json = json.loads(contents_gzip_deflated)

with open(JSON_FILE, 'w') as f:
    json_pretty = json.dumps(list_json, indent=4)
    f.write(json_pretty)

# ----- Parsing -----

list_title = list_json['name']

aggregates = {}

for entry in list_json['entries']:
    timestamp = entry['timestamp']
    rating = entry['rating']['value']

    dt = datetime.datetime.fromtimestamp(
        timestamp // 1000, tz=datetime.timezone.utc)
    start_of_day = dt.replace(hour=0, minute=0, second=0, microsecond=0)
    timestamp_sot = int(start_of_day.timestamp() * 1000)

    if timestamp_sot not in aggregates:
        aggregates[timestamp_sot] = {'sum': 0, 'count': 0}

    aggregates[timestamp_sot]['sum'] += rating
    aggregates[timestamp_sot]['count'] += 1

# ----- Averaging -----

averages = {}
for timestamp_sot, stats in aggregates.items():
    averages[timestamp_sot] = stats['sum'] / stats['count']

with open(AVERAGES_FILE, 'w') as f:
    json_pretty = json.dumps(averages, indent=4)
    f.write(json_pretty)

# ----- Graphing -----

data_points = []
for timestamp_sot, rating in averages.items():
    date = datetime.datetime.fromtimestamp(
        timestamp_sot // 1000, tz=datetime.timezone.utc)
    pretty_date = date.strftime('%Y/%m/%d')
    data_points.append((timestamp_sot, rating, pretty_date))

data_points.sort(key=lambda x: x[0])

# Uncomment to take last 30 days
# data_points = data_points[-30:]

x_values = [x[0] for x in data_points]
y_values = [x[1] for x in data_points]
x_labels = [x[2] for x in data_points]

xy_spline = make_interp_spline(x_values, y_values)
smooth_x_values = np.linspace(min(x_values), max(x_values), 500)
smooth_y_values = xy_spline(smooth_x_values)

plt.xticks(rotation=45, ha='right')
plt.plot(smooth_x_values, smooth_y_values)
plt.xticks(x_values, x_labels)
plt.yticks(
    [0, 1, 2, 3, 4],
    ['-2 Horrendous', '-1 Very bad', '+0 Not good', '+1 Decent', '+2 Excellent']
)
plt.subplots_adjust(bottom=0.2, left=0.2)
plt.savefig('graph.png')

plt.show()
