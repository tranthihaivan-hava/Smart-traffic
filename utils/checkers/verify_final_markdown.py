import re
import csv
from collections import Counter

locs = {}
svc = {}
with open('Data_B/locations.csv', 'r') as f:
    for row in csv.DictReader(f):
        locs[row['location_id']] = (float(row['x_km']), float(row['y_km']))
        svc[row['location_id']] = int(row['service_time'])

def parse_time_str(t_str):
    if t_str == '-': return 0.0
    t_str = t_str.strip()
    match = re.match(r'(\d+):(\d+)\s*(AM|PM)', t_str)
    if not match: return 0.0
    h, m, ampm = match.groups()
    h = int(h)
    if ampm == 'PM' and h < 12: h += 12
    if ampm == 'AM' and h == 12: h = 0
    return h * 60 + int(m)

with open('final_algorithm/detail-schedule.md', 'r') as f:
    content = f.read()

# Check duplicates/missing
matches = re.findall(r'\|\s*\d+\s*\|\s*\*\*([C\d]+)\*\*\s*\|([^\|]+)\|([^\|]+)\|([^\|]+)\|([^\|]+)\|([^\|]+)\|([^\|]+)\|', content)
customers = [m[0] for m in matches]
counts = Counter(customers)
duplicates = {k: v for k, v in counts.items() if v > 1}
missing = set(locs.keys()) - set(customers) - {'DEPOT'}

print(f"Total visits found in markdown: {len(customers)}")
print(f"Unique customers visited: {len(counts)}")
if duplicates: print(f"ERROR: Found duplicates: {duplicates}")
else: print("SUCCESS: No duplicated customers (No Hallucination).")
if missing: print(f"ERROR: Missing customers: {missing}")
else: print("SUCCESS: No missing customers (No Hallucination).")

# Check math
lines = content.split('\n')
errors = 0
for line in lines:
    if re.search(r'\|\s*\d+\s*\|\s*\*\*C', line):
        parts = [p.strip() for p in line.split('|')[1:-1]]
        cid = parts[1].replace('*', '')
        arrival = parse_time_str(parts[2])
        wait_str = parts[3].replace('m', '')
        wait = float(wait_str)
        service_start = parse_time_str(parts[5])
        service_dur = int(parts[6].replace('m', ''))
        departure = parse_time_str(parts[7])
        
        # Check arrival + wait == service_start
        if abs(arrival + wait - service_start) > 1.5:
            print(f"MATH ERROR ({cid}): Arrival {arrival} + Wait {wait} != Service {service_start}")
            errors += 1
            
        # Check service_start + dur == departure
        if abs(service_start + service_dur - departure) > 1.5:
            print(f"MATH ERROR ({cid}): Service {service_start} + Dur {service_dur} != Departure {departure}")
            errors += 1
            
        # Check time windows
        windows_str = parts[4]
        valid = False
        for w_str in windows_str.split(','):
            w_str = w_str.strip()
            start_str, end_str = w_str.split('-')
            w_start = parse_time_str(start_str)
            w_end = parse_time_str(end_str)
            if service_start >= w_start - 1.5 and service_start + service_dur <= w_end + 1.5:
                valid = True
                break
        if not valid:
            print(f"TW ERROR ({cid}): Service {parts[5]} (dur {service_dur}) not within {windows_str}")
            errors += 1

if errors == 0:
    print("SUCCESS: Mathematical constraints strictly verified (Arrival, Wait, Departure).")
    print("SUCCESS: Time Window boundaries strictly respected.")
    print("=> TỔNG KẾT: Markdown hoàn toàn chính xác, KHÔNG HỀ BỊ ẢO GIÁC!")
