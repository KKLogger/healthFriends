import json
import pandas

with open("data/분류기준 원료이름모음.txt", "r", encoding="utf-8-sig") as f:
    elements = f.read().split("\n")

with open("test.json", "r", encoding="utf-8-sig") as f:
    json_data = json.loads(f.read())

for item in json_data:
    for element in item:
        if element in elements:
            print(item)
