import random
import json
import os
from typing import List, Tuple
from models.problem import Problem
from models.state import State
from models.pending_queue import PendingQueue
from config.weights_config import WeightVector
from utils.route_validator import RouteValidator
from optimizer.repair_operator import RepairOperator
from solver.greedy_solver import GreedySolver
from models.candidate import Candidate
from solver.normalizer import Normalizer
from solver.score_calculator import ScoreCalculator

class GeneticHybridSolver:
    """
    Bayesian-Optimized Memetic Algorithm (BOMA)
    Combines:
    1. Solomon I1 & Bayesian Weights (for Seed Initialization)
    2. Genetic Algorithm (for Global Search)
    3. Fast Distance-based Decoder (for Sequence Mapping)
    4. Repair Operator (Ejection Pool for Local Search & Feasibility)
    """
    def __init__(self, problem: Problem, pop_size: int = 10, generations: int = 5, weights: WeightVector = None):
        self.problem = problem
        self.pop_size = pop_size
        self.generations = generations
        self.weights = weights if weights else WeightVector(1.0, 0.0, 0.0, 0.0)
        self.repair_operator = RepairOperator(problem)
        
        # All customers excluding DEPOT
        self.customers = [c.id for c in problem.get_all_customers() if c.id != "DEPOT"]



        self.normalizer = Normalizer()
        self.scorer = ScoreCalculator()
        
    def _generate_seed_chromosome(self) -> List[str]:
        """Runs the Greedy Bayesian Solver to generate a perfect initial seed sequence."""
        print("[HGA] Generating Bayesian Seed Chromosome...")
        greedy = GreedySolver(self.problem)
        state = greedy.solve_complete_problem(self.weights, use_local_search=False)
        
        seed = []
        for day in range(1, self.problem.max_days + 1):
            route = state.get_route(day)
            for c in route:
                if c != "DEPOT":
                    seed.append(c)
        
        unserved = state.pending_queue.get_pending()
        for c in unserved:
            if c not in seed:
                seed.append(c)
                
        return seed

    def solve(self, checkpoint_file: str = "hga_checkpoint.json", use_local_search: bool = False) -> State:
        print(f"[HGA] Initializing BOMA population of size {self.pop_size}...")
        
        # 1. Initialize or Load population
        population = None
        if os.path.exists(checkpoint_file):
            try:
                with open(checkpoint_file, 'r') as f:
                    saved_pop = json.load(f)
                if len(saved_pop) == self.pop_size:
                    population = saved_pop
                    print(f"[HGA] Loaded population from {checkpoint_file}. Resuming evolution!")
                else:
                    print(f"[HGA] Checkpoint size mismatch. Ignoring.")
            except Exception as e:
                print(f"[HGA] Error loading checkpoint: {e}. Starting fresh.")
                
        if population is None:
            population = [random.sample(self.customers, len(self.customers)) for _ in range(self.pop_size)]
            # Inject Bayesian Seed
            population[0] = self._generate_seed_chromosome()
        
        best_state = None
        best_fitness = float('inf')

        for gen in range(1, self.generations + 1):
            evaluated = []
            print(f"[HGA] Evaluating Generation {gen}/{self.generations}...")
            threshold_met = False
            for i, chromo in enumerate(population):
                state, fitness = self._decode(chromo)
                evaluated.append((chromo, state, fitness))
                
                if fitness < best_fitness:
                    best_fitness = fitness
                    best_state = state
                    unserved = len(state.pending_queue.get_pending())
                    dist = self._calc_total_distance(state)
                    print(f"      -> New Best Found! Unserved: {unserved}, Distance: {dist:.2f} km")
                    
                    # --- THRESHOLD ACCEPTANCE ---
                    if unserved <= 2:
                        print(f"      -> [Threshold] Đã đạt ngưỡng <= 2 đơn rớt. Chấp nhận kết quả sớm để chuyển sang Local Search!")
                        threshold_met = True
                        break
            
            if threshold_met:
                break
            
            # 2. Selection, Crossover, Mutation
            evaluated.sort(key=lambda x: x[2])
            
            # Elitism: keep top 2
            next_gen = [evaluated[0][0], evaluated[1][0]]
            
            while len(next_gen) < self.pop_size:
                p1 = self._tournament(evaluated)
                p2 = self._tournament(evaluated)
                c1 = self._crossover(p1, p2)
                self._mutate(c1)
                next_gen.append(c1)
                
            population = next_gen

        # 3. Save checkpoint for future runs
        try:
            with open(checkpoint_file, 'w') as f:
                json.dump(population, f)
            print(f"[HGA] Saved generation population to {checkpoint_file}!")
        except Exception as e:
            pass

        print(f"[HGA] Evolution complete. Best fitness: {best_fitness}")
        
        # --- TWO-PHASE OPTIMIZATION: POST-PROCESSING LOCAL SEARCH ---
        if use_local_search:
            unserved_count = len(best_state.pending_queue.get_pending())
            if unserved_count > 0:
                print(f"\n[Two-Phase Optimization] Áp dụng Local Search (Repair) để fix {unserved_count} đơn rớt...")
                self.repair_operator.run(best_state)
                final_unserved = len(best_state.pending_queue.get_pending())
                print(f"[Two-Phase Optimization] Hoàn tất Local Search! Số đơn rớt còn lại: {final_unserved}\n")
        # ------------------------------------------------------------
        
        return best_state

    def _tournament(self, evaluated: List[Tuple], k: int = 2) -> List[str]:
        candidates = random.sample(evaluated, k)
        return min(candidates, key=lambda x: x[2])[0]

    def _crossover(self, p1: List[str], p2: List[str]) -> List[str]:
        size = len(p1)
        c1 = [None] * size
        start, end = sorted(random.sample(range(size), 2))
        c1[start:end] = p1[start:end]
        p2_idx = 0
        for i in range(size):
            if c1[i] is None:
                while p2[p2_idx] in c1:
                    p2_idx += 1
                c1[i] = p2[p2_idx]
        return c1

    def _mutate(self, chromosome: List[str], mutation_rate: float = 0.2):
        if random.random() < mutation_rate:
            i, j = random.sample(range(len(chromosome)), 2)
            chromosome[i], chromosome[j] = chromosome[j], chromosome[i]

    def _decode(self, chromosome: List[str]) -> Tuple[State, float]:
        """
        The Decoder uses Bayesian Weights to intelligently score and pick the best insertion point.
        After decoding, it invokes the Memetic Repair operator to guarantee feasibility.
        """
        state = State(PendingQueue(set(self.customers)), self.problem.max_days)
        routes = {d: ["DEPOT"] for d in range(1, self.problem.max_days + 1)}
        max_days = self.problem.max_days
        
        for cid in chromosome:
            cust = self.problem.get_customer(cid)
            candidates = []
            
            for day in range(1, max_days + 1):
                windows = cust.get_windows_for_day(day)
                if not windows:
                    continue
                    
                route = routes[day]
                # Try inserting at every possible index in the day's route
                for i in range(1, len(route) + 1):
                    metrics = RouteValidator.validate_insertion(self.problem, cust, route, i, day)
                    if metrics is not None:
                        cand = Candidate(
                            customer_id=cid, 
                            day=day, 
                            insertion_index=i,
                            arrival_time=metrics["arrival_time"],
                            wait_time=metrics["wait_time"],
                            service_start_time=metrics["service_start_time"],
                            distance_delta=metrics["distance_delta"]
                        )
                        
                        # Urgency feature
                        active_window = None
                        for w in sorted(windows, key=lambda x: x.start_time):
                            if cand.arrival_time <= w.end_time:
                                active_window = w
                                break
                        win_end = active_window.end_time if active_window else 1440.0
                        f_urg = win_end - cand.arrival_time
                        
                        # Risk feature
                        all_windows = cust.get_all_windows()
                        remaining_wins = [w for w in all_windows if w.day >= day]
                        rem_count = len(remaining_wins) if len(remaining_wins) > 0 else 1
                        f_risk = 1.0 / (rem_count * (max_days - day + 1))
                        
                        cand.raw_features = {
                            "distance": cand.distance_delta,
                            "urgency": f_urg,
                            "waiting": cand.wait_time,
                            "delivery_risk": f_risk
                        }
                        candidates.append(cand)
            
            if candidates:
                self.normalizer.normalize(candidates)
                self.scorer.compute_scores(candidates, self.weights)
                best_cand = min(candidates, key=lambda c: c.score)
                routes[best_cand.day].insert(best_cand.insertion_index, cid)
                state.pending_queue.remove(cid)

        # Reconstruct the State object with the final routes
        for day, route in routes.items():
            if route[-1] != "DEPOT":
                route.append("DEPOT")
            state.set_route(day, route)
            
        # MEMETIC REPAIR PHASE
        unserved_count = len(state.pending_queue.get_pending())
        # if unserved_count > 0:
        #     # TẮT BÁC SĨ PHẪU THUẬT Ở ĐÂY VÌ ĐÃ CÓ POST-PROCESSING Ở CUỐI HÀM SOLVE
        #     # self.repair_operator.run(state)

        # Recalculate after repair
        unserved = len(state.pending_queue.get_pending())
        dist = self._calc_total_distance(state)
        
        # Fitness penalizes unserved customers heavily
        fitness = unserved * 100000.0 + dist
        return state, fitness

    def _calc_total_distance(self, state: State) -> float:
        total = 0.0
        for day in range(1, self.problem.max_days + 1):
            route = state.get_route(day)
            for i in range(len(route) - 1):
                total += self.problem.get_distance(route[i], route[i+1])
        return total
