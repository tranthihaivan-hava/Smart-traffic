import sys, os, time, json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from preprocessing.dataset_loader import DatasetLoader
from solver.baselines import BaselineSolver
from solver.genetic_hybrid import GeneticHybridSolver
from config.weights_config import WeightVector

def calculate_optimal_start_time(problem, route, day: int) -> float:
    if len(route) <= 2: return 480.0
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

def calculate_route_duration(problem, route, day: int) -> float:
    if len(route) <= 2: return 0.0
    start_time = calculate_optimal_start_time(problem, route, day)
    current_time = start_time
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
    return current_time - start_time

def evaluate_state(problem, state):
    total_dist = 0.0
    total_time = 0.0
    failed_orders = len(state.pending_queue.get_pending())
    
    for day in range(1, problem.max_days + 1):
        route = state.get_route(day)
        # Distance
        for i in range(len(route) - 1):
            total_dist += problem.get_distance(route[i], route[i+1])
        # Time
        total_time += calculate_route_duration(problem, route, day)
        
    return total_dist, total_time, failed_orders

def run_and_plot():
    print("Loading data...")
    loader = DatasetLoader()
    problem = loader.build_problem_instance("Data_B/locations.csv", "Data_B/time_windows.csv")

    algorithms = ["Baseline 1\n(NN)", "Baseline 2\n(EDF)", "Final\nAlgorithm"]
    colors = ['#E63946', '#F4A261', '#2A9D8F']
    
    distances = []
    times = []
    failed = []

    baseline = BaselineSolver(problem)

    # 1. NN
    print("Running Baseline 1 (Nearest Neighbor)...")
    nn_state = baseline.solve_nearest_neighbor()
    d, t, f = evaluate_state(problem, nn_state)
    distances.append(d)
    times.append(t / 60.0) # convert minutes to hours
    failed.append(f)

    # 2. EDF
    print("Running Baseline 2 (Earliest Deadline First)...")
    edf_state = baseline.solve_earliest_deadline_first()
    d, t, f = evaluate_state(problem, edf_state)
    distances.append(d)
    times.append(t / 60.0)
    failed.append(f)

    # 3. Final Algorithm (Loaded from checkpoint)
    print("Loading Final Algorithm from checkpoint...")
    import json
    from models.state import State
    from models.pending_queue import PendingQueue
    
    with open('Overview/presentation_result.txt', 'r') as f:
        routes_str = json.load(f)
        
    routes = {int(k): v for k, v in routes_str.items()}
    state = State(PendingQueue(set()), 7)
    for day in range(1, 8):
        if day in routes:
            state.set_route(day, routes[day])
    print("Loaded presentation_result.txt routes!")
        
    d, t, f = evaluate_state(problem, state)
    distances.append(d)
    times.append(t / 60.0)
    failed.append(f)

    # Make plots
    os.makedirs('Overview/visualize/Final', exist_ok=True)
    plt.rc('font', family='DejaVu Sans')

    def create_bar_chart(data, title, ylabel, filename):
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_facecolor('#F8F9FA')
        fig.patch.set_facecolor('#F8F9FA')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        bars = ax.bar(algorithms, data, color=colors, edgecolor='white', linewidth=1.2, zorder=3)
        for bar, val in zip(bars, data):
            # formatting
            if isinstance(val, float) and val > 1000:
                text = f"{val:,.0f}"
            elif isinstance(val, float):
                text = f"{val:.1f}"
            else:
                text = str(val)
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.02, text, 
                    ha='center', va='bottom', fontsize=12, fontweight='bold', color='#333')
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.35, zorder=0)
        
        # small padding on top to fit labels
        ax.set_ylim(0, max(data) * 1.15)

        plt.tight_layout()
        plt.savefig(f'Overview/visualize/Final/{filename}', dpi=180, bbox_inches='tight')
        plt.close()
        print(f"Saved {filename}")

    create_bar_chart(distances, 'Total Distance Comparison', 'Distance (km)', 'fig_compare_total_distance.png')
    create_bar_chart(times, 'Total Time Comparison', 'Time (Hours)', 'fig_compare_total_time.png')
    create_bar_chart(failed, 'Total Failed Orders Comparison', 'Number of Unserved Customers', 'fig_compare_failed_orders.png')
    print("Done!")

if __name__ == '__main__':
    run_and_plot()
