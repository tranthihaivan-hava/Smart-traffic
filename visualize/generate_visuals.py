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

routes = {
    1: 'C228,C175,C252,C106,C184,C288,C057,C056,C171,C072,C251,C071,C112,C214,C061,C017,C055,C224,C033,C148,C284,C249,C218,C294,C053,C182,C134,C276,C122,C194,C205,C204,C297,C088,C233,C064,C012,C058,C065,C045,C040,C237,C019,C286,C290,C051,C031,C257,C114,C085,C155,C280,C009'.split(','),
    2: 'C008,C110,C054,C179,C107,C068,C005,C152,C216,C135,C231,C059,C030,C217,C229,C291,C069,C274,C161,C300,C176,C100,C203,C187,C269,C198,C073,C075,C271,C126,C032,C256,C238,C260,C160,C151,C039,C006,C025,C255,C063,C236,C001,C197,C120,C163,C127,C157,C168,C062,C090,C108,C131,C103,C132,C278,C050,C195,C177,C097,C028'.split(','),
    3: 'C201,C258,C186,C015,C245,C141,C041,C034,C003,C086,C013,C102,C078,C239,C038,C154,C167,C192,C129,C247,C264,C162,C060,C084,C115,C265,C139,C299,C208,C125,C014,C082,C244,C273,C099,C281,C211,C036'.split(','),
    4: 'C140,C016,C227,C242,C215,C241,C052,C101,C092,C232,C285,C124,C046,C275,C223,C283,C166,C158,C081,C243,C150,C144,C044,C246,C266,C143,C206,C174,C096,C221,C010,C022,C089,C259,C191,C091,C007,C248,C235,C095,C298,C136,C165,C289,C149,C067,C111,C267,C210,C270'.split(','),
    5: 'C024,C002,C147,C156,C117,C296,C130,C230,C077,C119,C098,C183,C070,C268,C295,C180,C202,C137,C128,C076,C250,C287,C023,C170,C146,C181,C105'.split(','),
    6: 'C169,C145,C209,C188,C049,C109,C037,C153,C138,C178,C066,C253,C207,C018,C123,C080,C172,C282,C093,C199,C254,C225,C004,C164,C047,C263,C185,C159,C087,C027,C116,C035,C094,C272,C026,C043,C226,C213,C222,C074,C220,C121'.split(','),
    7: 'C011,C133,C212,C029,C293,C193,C262,C200,C079,C196,C240,C279,C020,C021,C292,C118,C261,C219,C104,C142,C042,C277,C113,C234,C190,C173,C189'.split(','),
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
ax.set_title('Number of Customers Served per Day  (Total: 298 / 300)', fontsize=13, fontweight='bold', pad=10)
ax.set_ylabel('Customers Served', fontsize=11)
ax.grid(axis='y', linestyle='--', alpha=0.35, zorder=0)
plt.tight_layout()
plt.savefig('visualize/fig2_daily_counts.png', dpi=180, bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# FIG 3 — Method Comparison
# -------------------------------------------------------------
print("Generating Fig 3: Method Comparison...")
methods       = ['Nearest\nNeighbor', 'Earliest\nDeadline First', 'Proposed\n(Default w)', 'Proposed\n(Optuna w)']
unserved_vals = [102, 13, 7, 2]
loss_vals     = [1021581, 130420, 70810, 23581]
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
ax1.set_ylim(0, 115)
ax1.grid(axis='y', linestyle='--', alpha=0.35, zorder=0)

bars2 = ax2.bar(methods, loss_vals, color=colors_bar, edgecolor='white', linewidth=1, zorder=3)
for b, v in zip(bars2, loss_vals):
    ax2.text(b.get_x()+b.get_width()/2, b.get_height()*1.03, f'{v:,.0f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
ax2.set_yscale('log')
ax2.set_title('Objective Loss Score  (log scale)', fontsize=12, fontweight='bold', pad=8)
ax2.set_ylabel('Loss Score', fontsize=10)
ax2.grid(axis='y', linestyle='--', alpha=0.35, zorder=0)

fig.suptitle('Algorithm Comparison: 4 Methods', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('visualize/fig3_comparison.png', dpi=180, bbox_inches='tight')
plt.close()

# -------------------------------------------------------------
# FIG 4 — Shift Timeline
# -------------------------------------------------------------
print("Generating Fig 4: Shift Timeline...")
start_min  = 480   # 08:00
return_min = {1:1311, 2:1308.6, 3:1290.6, 4:1315.7, 5:1308, 6:1017.3, 7:867}

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
ax.set_title('Daily Shipper Shift Timeline  (Departure → Return to Depot)', fontsize=13, fontweight='bold', pad=10)
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

ax.set_title('Customer Distribution Across the Week\n(Total: 300 customers)', fontsize=13, fontweight='bold', pad=14)
plt.tight_layout()
plt.savefig('visualize/fig5_distribution_pie.png', dpi=180, bbox_inches='tight')
plt.close()

print("All charts updated and saved successfully!")
