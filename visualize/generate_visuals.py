import sys, os, csv, math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
from matplotlib.colors import to_rgba
import numpy as np

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

# STRICT TIME WINDOW APPROACH – Optuna Optimized Routes
routes = {
    1: 'C175,C228,C247,C110,C174,C206,C107,C179,C005,C143,C119,C144,C150,C135,C216,C152,C243,C291,C265,C158,C166,C178,C063,C154,C167,C187,C129,C236,C059,C081,C030,C115,C197,C180,C261,C139,C299,C120,C142,C014,C049,C062,C234,C270,C188,C108,C125,C210,C202,C132,C209,C267'.split(','),
    2: 'C269,C231,C162,C229,C274,C176,C203,C198,C008,C148,C245,C294,C122,C276,C141,C284,C015,C033,C017,C003,C112,C013,C102,C073,C255,C025,C161,C006,C021,C183,C215,C256,C260,C160,C151,C032,C126,C271,C075,C300,C039,C238,C295,C165,C136,C123,C097,C253,C028,C278,C169,C051,C181,C211,C040,C170,C114,C085,C280'.split(','),
    3: 'C288,C056,C061,C086,C224,C218,C053,C182,C134,C034,C297,C041,C186,C258,C252,C106,C184,C201,C264,C044,C060,C084,C068,C192,C217,C069,C100,C078,C171,C071,C204,C205,C194,C146,C237,C023,C287,C257,C031,C250,C009,C011,C116,C027,C262,C263,C200,C036,C189'.split(','),
    4: 'C140,C057,C055,C214,C251,C072,C016,C227,C242,C052,C241,C232,C285,C124,C046,C275,C223,C283,C096,C054,C246,C077,C022,C010,C221,C092,C101,C239,C038,C067,C111,C149,C289,C298,C095,C235,C248,C007,C091,C089,C168,C099,C281'.split(','),
    5: 'C230,C130,C296,C117,C156,C147,C002,C249,C024,C070,C098,C163,C001,C190,C131,C137,C173,C128,C083,C076,C233,C272'.split(','),
    6: 'C145,C207,C018,C199,C254,C225,C004,C164,C282,C093,C172,C191,C080,C259,C066,C138,C177,C050,C195,C103,C090,C153,C208,C037,C127,C157,C109,C266,C220,C121,C074,C213,C222,C159,C185,C047,C087,C226,C065,C043,C026,C155,C094,C035,C290,C105'.split(','),
    7: 'C113,C082,C244,C273,C277,C042,C104,C219,C118,C292,C020,C279,C240,C196,C079,C193,C012,C293,C064,C029,C212,C133,C088,C058,C045,C019,C286'.split(','),
}
unserved = ['C048', 'C083']
day_counts = {d: len(r) for d, r in routes.items()}

cust_day = {}
for d, r in routes.items():
    for c in r:
        cust_day[c] = d

# -------------------------------------------------------------
# FIG 1 — Route Map
# -------------------------------------------------------------
print("Generating Fig 1: Route Map...")
fig, ax = plt.subplots(figsize=(14, 11))
ax.set_facecolor('#F8F9FA')
fig.patch.set_facecolor('#F8F9FA')

depot = locs['DEPOT']
for day, route in routes.items():
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
legend_elements += [Line2D([0],[0], marker='x', color='#333', linestyle='None', markersize=8, markeredgewidth=2, label='Unserved (2)'),
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
ax.set_title('Number of Customers Served per Day  (Total: 298 / 300)  [Strict Windows]', fontsize=13, fontweight='bold', pad=10)
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
methods       = ['Nearest\nNeighbor', 'Earliest\nDeadline First', 'Proposed\n(Default w)', 'Proposed\n(Optuna w)']
unserved_vals = [115, 15, 22, 2]
loss_vals     = [1153772, 153684, 223616, 23565]
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
start_min  = 480   # 08:00
# STRICT TIME WINDOW return times
return_min = {1:1281.0, 2:1272.2, 3:1281.3, 4:1243.6, 5:1251.5, 6:1275.2, 7:1271.3}

def fmt(m):
    return f'{int(m)//60:02d}:{int(m)%60:02d}'

fig, ax = plt.subplots(figsize=(12, 5))
ax.set_facecolor('#F8F9FA')
fig.patch.set_facecolor('#F8F9FA')

for i, day in enumerate(range(1, 8)):
    ret = return_min[day]
    duration = ret - start_min
    bar = ax.barh(i, duration, left=start_min, color=DAY_COLORS[day], height=0.55, edgecolor='white', linewidth=0.8, zorder=3)
    ax.text(start_min + duration/2, i, f'{fmt(start_min)} – {fmt(ret)}  ({duration/60:.1f}h)', ha='center', va='center', fontsize=8.5, fontweight='bold', color='white' if duration > 300 else '#333')

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

sizes   = [day_counts[d] for d in range(1, 8)] + [2]
labels  = [f'{DAY_NAMES[d]}\n{day_counts[d]}' for d in range(1, 8)] + ['Unserved\n2']
colors  = [DAY_COLORS[d] for d in range(1, 8)] + ['#555555']
explode = [0.03]*7 + [0.12]

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
