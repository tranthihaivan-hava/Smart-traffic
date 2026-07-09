# 08 — `visualize/` Folder Guide

## Purpose

A **standalone script** that generates 5 publication-quality PNG charts  
summarizing the optimization results. It is NOT called by `main.py` —  
run it separately after the solver has been executed.

```bash
python visualize/generate_visuals.py
```

---

## Files

---

### `generate_visuals.py`

All chart code lives in this single file.  
It uses **matplotlib** with a consistent `#F8F9FA` light-grey background theme.

---

## The 5 Figures

---

### Figure 1 — `fig1_route_map.png` — Route Map

**What it shows:** A 2D scatter plot of all customer locations,  
with the routes for each day drawn as colored lines.

- Each day gets a unique color
- The DEPOT is marked prominently at the center
- Customer stops are plotted as dots at their (x, y) coordinates
- Lines connect each stop in route order

**Purpose:** Visual sanity check — are routes geographically reasonable?  
Do they cross unnecessarily, or are they well-organized clusters?

---

### Figure 2 — `fig2_daily_counts.png` — Daily Customer Counts

**What it shows:** A bar chart with one bar per day (Mon–Sun),  
showing how many customers were served on that day.

**Purpose:** Check if the load is balanced across the week  
or if most customers are packed into one or two days.

---

### Figure 3 — `fig3_comparison.png` — Solver Comparison

**What it shows:** A grouped bar chart comparing our **Greedy + Bayesian** solver  
against the two baseline solvers:
- Nearest Neighbor
- Earliest Deadline First

Bars show: failed deliveries, total distance, total waiting time, and loss score.

**Purpose:** Demonstrate that the optimized solver outperforms simple heuristics.

---

### Figure 4 — `fig4_shift_timeline.png` — Shift Timeline (Gantt)

**What it shows:** A horizontal Gantt-style chart.  
Each day is a row. Each customer stop is a colored bar showing when service happens  
(from service_start_time to service_start_time + service_duration).

**Purpose:** Visualize the vehicle's daily schedule — where it spends its time,  
when it waits, and how tight the schedule is.

---

### Figure 5 — `fig5_distribution_pie.png` — Customer Distribution Pie

**What it shows:** A pie chart showing what percentage of customers  
were served on each day of the week. An "Unserved" slice is included if any customers were missed.

**Purpose:** High-level overview of how work is distributed across the week.

---

## Chart Style Conventions

All figures use a consistent visual style:

| Setting | Value |
|---|---|
| Background | `#F8F9FA` (light grey) |
| Font | System default (serif/sans) |
| Day colors | 7 distinct colors per day (defined in `DAY_COLORS` dict) |
| Figure size | Varies: typically `(9, 7)` or `(12, 6)` |

---

## Important Note: Type Annotation Fix

`ax.pie()` in matplotlib has an overloaded return type:
- Without `autopct`: returns `(wedges, texts)`  — 2-tuple
- With `autopct`: returns `(wedges, texts, autotexts)` — 3-tuple

The type checker (Pylance) cannot infer which one is used at compile time,  
so the code uses an explicit annotation to avoid the error:

```python
pie_result: tuple[list, list, list] = ax.pie(  # type: ignore[assignment]
    sizes, ..., autopct='%1.1f%%', ...
)
wedges, texts, autotexts = pie_result
```

This is a **type-annotation-only fix** — at runtime, it always returns 3 values  
because `autopct` is always provided.
