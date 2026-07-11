from typing import List, Dict, Any, Optional
from models.problem import Problem
from models.customer import Customer

class RouteValidator:
    @staticmethod
    def validate_insertion(problem: Problem, customer: Customer, route: List[str], index: int, day: int) -> Optional[Dict[str, Any]]:
        """
        Kiểm tra xem việc chèn khách hàng 'customer' vào vị trí 'index' trong 'route' của ngày 'day' có khả thi không.
        Nếu khả thi, trả về một dictionary chứa các thông số:
        - distance_delta: Sự thay đổi về quãng đường (c1_cost).
        - arrival_time: Thời gian đến.
        - wait_time: Thời gian chờ.
        - service_start_time: Thời gian bắt đầu phục vụ.
        Nếu không khả thi, trả về None.
        """
        # Form the proposed new route
        new_route = list(route)
        new_route.insert(index, customer.id)
        
        # Ensure we always end at DEPOT when calculating timeline
        if new_route[-1] != "DEPOT":
            new_route.append("DEPOT")

        # 1. Capacity check
        total_demand = sum(problem.get_customer(cid).demand for cid in new_route if cid != "DEPOT")
        if total_demand > problem.vehicle_capacity:
            return None

        # 2. Timeline validation
        current_time = 0.0
        prev_id = "DEPOT"
        
        target_arrival = None
        target_wait = None
        target_service_start = None

        for i, cid in enumerate(new_route):
            if i == 0:
                continue
            
            travel_time = problem.get_travel_time(prev_id, cid)
            arrival = current_time + travel_time
            
            if cid == "DEPOT":
                current_time = arrival
                prev_id = cid
                continue
                
            cust = problem.get_customer(cid)
            windows = cust.get_windows_for_day(day)
            
            # Find a valid window we can satisfy
            # Strict rule: entire service (start + duration) must finish within the window
            valid_window = None
            for w in sorted(windows, key=lambda x: x.start_time):
                service_start_cand = max(arrival, w.start_time)
                service_end_cand = service_start_cand + cust.service_duration
                if service_end_cand <= w.end_time:
                    valid_window = w
                    break
            
            if valid_window is None:
                # Infeasible
                return None
                
            wait = max(0.0, valid_window.start_time - arrival)
            service_start = arrival + wait
            service_end = service_start + cust.service_duration
            
            if cid == customer.id and i == index:
                target_arrival = arrival
                target_wait = wait
                target_service_start = service_start
                
            current_time = service_end
            prev_id = cid

        # If we reached here, simulation is feasible!
        # 3. Calculate distance detour: d_{i,u} + d_{u,j} - d_{i,j}
        # where i = new_route[index-1], u = customer.id, j = new_route[index+1]
        i_id = new_route[index - 1]
        j_id = new_route[index + 1]
        d_iu = problem.get_distance(i_id, customer.id)
        d_uj = problem.get_distance(customer.id, j_id)
        d_ij = problem.get_distance(i_id, j_id)
        distance_delta = d_iu + d_uj - d_ij

        return {
            "distance_delta": distance_delta,
            "arrival_time": target_arrival,
            "wait_time": target_wait,
            "service_start_time": target_service_start
        }
