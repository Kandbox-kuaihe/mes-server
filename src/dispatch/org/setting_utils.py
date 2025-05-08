import json
from pathlib import Path


def read_setting_json():
    cur_path = Path(__file__).resolve().parent
    with open(cur_path / '../static/settings.json', 'r') as file:
        return json.load(file)


if __name__ == "__main__":
    print(read_setting_json())
