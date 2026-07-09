from typing import List
from models.candidate import Candidate
from config.weights_config import WeightVector

class ScoreCalculator:
    def compute_scores(self, candidates: List[Candidate], weights: WeightVector) -> None:
        for cand in candidates:
            w_dist = weights.distance
            w_urg = weights.urgency
            w_wait = weights.waiting
            w_risk = weights.delivery_risk
            
            score = (
                w_dist * cand.norm_features["distance"] +
                w_urg * cand.norm_features["urgency"] +
                w_wait * cand.norm_features["waiting"] +
                w_risk * cand.norm_features["delivery_risk"]
            )
            cand.score = score
