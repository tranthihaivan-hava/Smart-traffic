from typing import List
from models.problem import Problem
from models.state import State
from models.candidate import Candidate

class FeatureExtractor:
    def __init__(self, problem: Problem):
        self._problem = problem

    def extract_features(self, candidates: List[Candidate], state: State, day: int):
        current_time = state.current_time
        max_days = self._problem.max_days

        for cand in candidates:
            cust = self._problem.get_customer(cand.customer_id)
            windows = cust.get_windows_for_day(day)
            
            # Find the active window corresponding to arrival_time
            active_window = None
            for w in sorted(windows, key=lambda x: x.start_time):
                if cand.arrival_time <= w.end_time:
                    active_window = w
                    break
            
            # Fallback in case window not found
            win_end = active_window.end_time if active_window is not None else 1440.0
            
            # 1. Distance Cost
            f_dist = cand.distance_delta
            
            # 2. Urgency
            f_urg = win_end - current_time
            
            # 3. Waiting Time
            f_wait = cand.wait_time
            
            # 4. Delivery Risk
            # Remaining windows from current day onwards
            all_windows = cust.get_all_windows()
            remaining_wins = [w for w in all_windows if w.day >= day]
            rem_count = len(remaining_wins) if len(remaining_wins) > 0 else 1
            
            f_risk = 1.0 / (rem_count * (max_days - day + 1))
            
            cand.raw_features = {
                "distance": f_dist,
                "urgency": f_urg,
                "waiting": f_wait,
                "delivery_risk": f_risk
            }
