import optuna
from typing import Optional, Dict
from models.problem import Problem
from solver.greedy_solver import GreedySolver
from optimizer.objective_function import ObjectiveFunction
from config.weights_config import WeightVector

class BayesianOptimizer:
    def __init__(
        self,
        problem: Problem,
        solver: GreedySolver,
        objective_evaluator: ObjectiveFunction
    ):
        self._problem = problem
        self._solver = solver
        self._evaluator = objective_evaluator
        self._study: Optional[optuna.study.Study] = None

    def optimize(self, n_trials: int = 500) -> WeightVector:
        # Create a study to minimize the objective loss
        # Use TPE sampler (default for optuna.create_study)
        optuna.logging.set_verbosity(optuna.logging.WARNING)
        self._study = optuna.create_study(direction="minimize")
        
        self._study.optimize(self._objective_wrapper, n_trials=n_trials)
        
        # Get best parameters
        best_params = self._study.best_params
        best_vector = WeightVector(
            distance=best_params["distance"],
            urgency=best_params["urgency"],
            waiting=best_params["waiting"],
            delivery_risk=best_params["delivery_risk"]
        )
        return best_vector

    def get_best_objective(self) -> float:
        if self._study is None:
            return float('inf')
        return self._study.best_value

    def get_study(self) -> optuna.study.Study:
        return self._study

    def _objective_wrapper(self, trial: optuna.trial.Trial) -> float:
        # Suggest weights in range [0.0, 1.0]
        distance = trial.suggest_float("distance", 0.0, 1.0)
        urgency = trial.suggest_float("urgency", 0.0, 1.0)
        waiting = trial.suggest_float("waiting", 0.0, 1.0)
        delivery_risk = trial.suggest_float("delivery_risk", 0.0, 1.0)

        weights = WeightVector(
            distance=distance,
            urgency=urgency,
            waiting=waiting,
            delivery_risk=delivery_risk
        )

        # Run inner-loop solver (disable local search for speed during trials)
        state = self._solver.solve_complete_problem(weights, use_local_search=False)
        
        # Return loss value
        return self._evaluator.evaluate(state, self._problem)

