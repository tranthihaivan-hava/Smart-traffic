import sys, os, csv, math
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib.colors import to_rgba
import numpy as np

from preprocessing.dataset_loader import DatasetLoader
from solver.greedy_solver import GreedySolver
from config.weights_config import WeightVector
from config.settings import get_settings

# Create visualize directory
os.makedirs('visualize', exist_ok=True)

# Colors and names configuration
DAY_COLORS = {
    1: '#E63946',  # Monday    – vivid red
    2: '#F4A261',  # Tuesday   – orange
    3: '#2A9D8F',  # Wednesday – teal
    4: '#457B9D',  # Thursday  – steel blue
    5: '#6A4C93',  # Friday    – purple
    6: '#4CC9F0',  # Saturday  – sky
    7: '#06D6A0',  # Sunday    – mint
}
DAY_NAMES = {1:'Monday',2:'Tuesday',3:'Wednesday',4:'Thursday',
             5:'Friday',6:'Saturday',7:'Sunday'}

plt.rc('font', family='DejaVu Sans')
plt.rcParams.update({'axes.spines.top': False, 'axes.spines.right': False})

# Load CSV data
BASE = 'Data_B'
locs = {}
svc  = {}
with open(f'{BASE}/locations.csv', newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        locs[row['location_id']] = (float(row['x_km']), float(row['y_km']))
        svc[row['location_id']]  = int(row['service_time'])

print("Running solver to get actual routes...")
loader = DatasetLoader()
problem = loader.build_problem_instance("Data_B/locations.csv", "Data_B/time_windows.csv")
solver = GreedySolver(problem)
weights = WeightVector(distance=0.04937285751085062, urgency=0.7116648907564567, waiting=0.48155705278840216, delivery_risk=0.9061216371003185)
state = solver.solve_complete_problem(weights)

raw_routes = state.get_completed_routes()
routes = {}
for d, r in raw_routes.items():
    if len(r) > 2:
        routes[d] = r[1:-1] # strip DEPOT
    else:
        routes[d] = []

unserved = list(state.pending_queue.get_pending())
day_counts = {d: len(r) for d, r in routes.items()}

cust_day = {}
for d, r in routes.items():
    for c in r:
        cust_day[c] = d

def calculate_optimal_start_time(problem, route, day: int) -> float:
    """Tự động tính giờ xuất phát tối ưu cho mỗi ngày."""
    if len(route) <= 2:
        return 480.0
        
    first_cust = route[1]
    tt = problem.get_travel_time("DEPOT", first_cust)
    cust = problem.get_customer(first_cust)
    windows = cust.get_windows_for_day(day)
    
    valid_window = None
    for w in sorted(windows, key=lambda x: x.start_time):
        if max(tt, w.start_time) + cust.service_duration <= w.end_time:
            valid_window = w
            break
            
    if valid_window:
        max_depart = valid_window.start_time - tt
        return max(0.0, (max_depart // 10) * 10)
    return 0.0

# -------------------------------------------------------------
# FIG 1 — Route Map
# -------------------------------------------------------------
print("Generating Fig 1: Route Map...")
fig, ax = plt.subplots(figsize=(14, 11))
ax.set_facecolor('#F8F9FA')
fig.patch.set_facecolor('#F8F9FA')

depot = locs['DEPOT']
for day, route in routes.items():
    if not route: continue
    color = DAY_COLORS[day]
    seq = ['DEPOT'] + route + ['DEPOT']
    xs = [locs[c][0] for c in seq]
    ys = [locs[c][1] for c in seq]
    ax.plot(xs, ys, color=color, alpha=0.25, linewidth=0.7, zorder=1)

for cid, (x, y) in locs.items():
    if cid == 'DEPOT':
        continue
    if cid in unserved:
        ax.scatter(x, y, c='#333333', s=55, marker='x', linewidths=1.8, zorder=4)
    else:
        day = cust_day.get(cid, 0)
        if day == 0:
            ax.scatter(x, y, c='#333333', s=55, marker='x', linewidths=1.8, zorder=4)
        else:
            ax.scatter(x, y, c=DAY_COLORS[day], s=28, alpha=0.85, zorder=3, edgecolors='white', linewidths=0.3)

ax.scatter(*depot, c='#FFD700', s=280, marker='*', zorder=6, edgecolors='#333', linewidths=0.8, label='Depot')

legend_elements  = [mpatches.Patch(facecolor=DAY_COLORS[d], label=f'{DAY_NAMES[d]} ({day_counts[d]})') for d in range(1, 8)]
legend_elements += [Line2D([0],[0], marker='x', color='#333', linestyle='None', markersize=8, markeredgewidth=2, label=f'Unserved ({len(unserved)})'),
                    Line2D([0],[0], marker='*', color='#FFD700', linestyle='None', markersize=12, markeredgecolor='#333', label='Depot')]
ax.legend(handles=legend_elements, loc='upper left', fontsize=9, framealpha=0.9, edgecolor='#ccc')

ax.set_title('Weekly Delivery Route Map  –  300 Customers, 7 Days', fontsize=14, fontweight='bold', pad=12)
ax.set_xlabel('X coordinate (km)', fontsize=10)
ax.set_ylabel('Y coordinate (km)', fontsize=10)
ax.grid(True, linestyle='--', alpha=0.3, color='#aaa')
plt.tight_layout()
plt.savefig('visualize/fig1_route_map.png', dpi=180, bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# FIG 2 — Daily Customer Count Bar Chart
# -------------------------------------------------------------
print("Generating Fig 2: Daily Customer Count...")
fig, ax = plt.subplots(figsize=(10, 5.5))
ax.set_facecolor('#F8F9FA')
fig.patch.set_facecolor('#F8F9FA')

days = list(range(1, 8))
counts = [day_counts[d] for d in days]
bars = ax.bar([DAY_NAMES[d] for d in days], counts, color=[DAY_COLORS[d] for d in days], edgecolor='white', linewidth=1.2, zorder=3)
for bar, val in zip(bars, counts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.8, str(val), ha='center', va='bottom', fontsize=12, fontweight='bold', color='#333')

ax.axhline(sum(counts)/7, color='#888', linestyle='--', linewidth=1.2, label=f'Average ({sum(counts)/7:.0f})')
ax.legend(fontsize=10, framealpha=0.9)
ax.set_ylim(0, max(counts) + 10)
total_served = 300 - len(unserved)
ax.set_title(f'Number of Customers Served per Day  (Total: {total_served} / 300)  [Strict Windows]', fontsize=13, fontweight='bold', pad=10)
ax.set_ylabel('Customers Served', fontsize=11)
ax.grid(axis='y', linestyle='--', alpha=0.35, zorder=0)
plt.tight_layout()
plt.savefig('visualize/fig2_daily_counts.png', dpi=180, bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# FIG 3 — Method Comparison
# -------------------------------------------------------------
print("Generating Fig 3: Method Comparison...")
# STRICT TIME WINDOW comparison values
methods       = ['Nearest\nNeighbor', 'Earliest\nDeadline First', 'Proposed\n(Default w)', 'Proposed\n+ Repair (Ejection)']
unserved_vals = [115, 15, 22, 0]
loss_vals     = [1153772, 153684, 223616, 3666]
colors_bar    = ['#E63946', '#F4A261', '#457B9D', '#06D6A0']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.5))
for ax in (ax1, ax2):
    ax.set_facecolor('#F8F9FA')
fig.patch.set_facecolor('#F8F9FA')

bars1 = ax1.bar(methods, unserved_vals, color=colors_bar, edgecolor='white', linewidth=1, zorder=3)
for b, v in zip(bars1, unserved_vals):
    ax1.text(b.get_x()+b.get_width()/2, b.get_height()+0.8, str(v), ha='center', va='bottom', fontweight='bold', fontsize=12)
ax1.set_title('Unserved Customers', fontsize=12, fontweight='bold', pad=8)
ax1.set_ylabel('Count', fontsize=10)
ax1.set_ylim(0, 130)
ax1.grid(axis='y', linestyle='--', alpha=0.35, zorder=0)

bars2 = ax2.bar(methods, loss_vals, color=colors_bar, edgecolor='white', linewidth=1, zorder=3)
for b, v in zip(bars2, loss_vals):
    ax2.text(b.get_x()+b.get_width()/2, b.get_height()*1.03, f'{v:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
ax2.set_yscale('log')
ax2.set_title('Objective Loss Score  (log scale)', fontsize=12, fontweight='bold', pad=8)
ax2.set_ylabel('Loss Score', fontsize=10)
ax2.grid(axis='y', linestyle='--', alpha=0.35, zorder=0)

fig.suptitle('Algorithm Comparison: 4 Methods  [Strict Windows]', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('visualize/fig3_comparison.png', dpi=180, bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# FIG 4 — Shift Timeline
# -------------------------------------------------------------
print("Generating Fig 4: Shift Timeline...")
# Remove global start_min here, we will track minimum start_time across all days
# to set the plot axis limits appropriately
shift_starts = {}
for day in range(1, 8):
    shift_starts[day] = calculate_optimal_start_time(problem, raw_routes[day], day)
    
start_min = min(shift_starts.values()) - 30 # For plotting axis

# Calculate return times based on actual solved state
return_min = {}
for day in range(1, 8):
    route = raw_routes[day]
    current_time = shift_starts[day]
    prev_id = "DEPOT"
    for i, cid in enumerate(route):
        if i == 0: continue
        tt = problem.get_travel_time(prev_id, cid)
        arrival = current_time + tt
        if cid == "DEPOT":
            current_time = arrival
            break
        cust = problem.get_customer(cid)
        windows = cust.get_windows_for_day(day)
        valid_window = None
        for w in sorted(windows, key=lambda x: x.start_time):
            service_start_cand = max(arrival, w.start_time)
            service_end_cand = service_start_cand + cust.service_duration
            if service_end_cand <= w.end_time:
                valid_window = w
                break
        wait = max(0.0, valid_window.start_time - arrival) if valid_window else 0.0
        service_start = arrival + wait
        current_time = service_start + cust.service_duration
        prev_id = cid
    return_min[day] = current_time - shift_starts[day]  # duration of this day's shift

def fmt(m):
    return f'{int(m)//60:02d}:{int(m)%60:02d}'

fig, ax = plt.subplots(figsize=(12, 5))
ax.set_facecolor('#F8F9FA')
fig.patch.set_facecolor('#F8F9FA')

for i, day in enumerate(range(1, 8)):
    start_time = shift_starts[day]
    end_time = start_time + return_min[day]
    color = DAY_COLORS[day]
    ax.barh(i, return_min[day], left=start_time, height=0.55, color=color, alpha=0.8, edgecolor='white', zorder=3)
    
    # Put text inside the bar to avoid overlap with y-axis labels
    center_x = start_time + (return_min[day] / 2)
    duration_h = return_min[day] / 60.0
    text_color = 'white' if return_min[day] > 180 else '#333333' # Dùng chữ trắng nếu thanh dài, đen nếu thanh quá ngắn
    ax.text(center_x, i, f'{fmt(start_time)} – {fmt(end_time)} ({duration_h:.1f}h)', 
            va='center', ha='center', fontsize=9, fontweight='bold', color=text_color)

ax.set_yticks(range(7))
ax.set_yticklabels([f'{DAY_NAMES[d]}  ({day_counts[d]} cust.)' for d in range(1,8)], fontsize=10)
ax.set_xticks(range(480, 1380, 60))
ax.set_xticklabels([fmt(m) for m in range(480, 1380, 60)], fontsize=8, rotation=45)
ax.set_xlim(420, 1380)
ax.set_xlabel('Time of Day', fontsize=10)
ax.set_title('Daily Shipper Shift Timeline  [Strict Windows]  (Departure → Return to Depot)', fontsize=13, fontweight='bold', pad=10)
ax.grid(axis='x', linestyle='--', alpha=0.3, zorder=0)
plt.tight_layout()
plt.savefig('visualize/fig4_shift_timeline.png', dpi=180, bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# FIG 5 — Pie Chart
# -------------------------------------------------------------
print("Generating Fig 5: Customer Distribution Pie...")
fig, ax = plt.subplots(figsize=(9, 7))
fig.patch.set_facecolor('#F8F9FA')
ax.set_facecolor('#F8F9FA')

if len(unserved) > 0:
    sizes   = [day_counts[d] for d in range(1, 8)] + [len(unserved)]
    labels  = [f'{DAY_NAMES[d]}\n{day_counts[d]}' for d in range(1, 8)] + [f'Unserved\n{len(unserved)}']
    colors  = [DAY_COLORS[d] for d in range(1, 8)] + ['#555555']
    explode = [0.03]*7 + [0.12]
else:
    sizes   = [day_counts[d] for d in range(1, 8)]
    labels  = [f'{DAY_NAMES[d]}\n{day_counts[d]}' for d in range(1, 8)]
    colors  = [DAY_COLORS[d] for d in range(1, 8)]
    explode = [0.03]*7

pie_result: tuple[list, list, list] = ax.pie(  # type: ignore[assignment]
    sizes, labels=labels, colors=colors, explode=explode,
    autopct='%1.1f%%', startangle=140, pctdistance=0.78,
    textprops={'fontsize': 9.5}
)
wedges, texts, autotexts = pie_result
for at in autotexts:
    at.set_fontsize(8.5)
    at.set_color('white')
    at.set_fontweight('bold')

ax.set_title('Customer Distribution Across the Week  [Strict Windows]\n(Total: 300 customers)', fontsize=13, fontweight='bold', pad=14)
plt.tight_layout()
plt.savefig('visualize/fig5_distribution_pie.png', dpi=180, bbox_inches='tight')
plt.close()

print("All charts updated and saved successfully!")
