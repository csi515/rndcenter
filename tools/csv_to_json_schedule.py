import csv
import json
import os

csv_path = os.path.join('data', 'schedule.csv')
json_path = os.path.join('data', 'schedule.json')

with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    data = list(reader)

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'변환 완료: {json_path}') 