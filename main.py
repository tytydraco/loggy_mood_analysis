import os
import base64
import gzip
import json

CWD = os.path.dirname(os.path.realpath(__file__))
INPUT_FILE = f'{CWD}/input.txt'
JSON_FILE = f'{CWD}/list.json'

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
    print(json_pretty)
