import csv
from typing import List, Dict
from utils.validators import validate_location_row, validate_window_row

class CSVLoader:
    def load_locations(self, filepath: str) -> List[Dict[str, str]]:
        data = []
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cleaned = {k.strip(): v.strip() for k, v in row.items()}
                validate_location_row(cleaned)
                data.append(cleaned)
        return data

    def load_time_windows(self, filepath: str) -> List[Dict[str, str]]:
        data = []
        with open(filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cleaned = {k.strip(): v.strip() for k, v in row.items()}
                validate_window_row(cleaned)
                data.append(cleaned)
        return data

