from typing import List
from models.candidate import Candidate

class Normalizer:
    def __init__(self, epsilon: float = 1e-6):
        self.epsilon = epsilon

    def normalize(self, candidates: List[Candidate]):
        if not candidates:
            return

        features = ["distance", "urgency", "waiting", "delivery_risk"]
        
        # Calculate min and max for each feature
        min_vals = {}
        max_vals = {}
        
        for feat in features:
            vals = [cand.raw_features[feat] for cand in candidates]
            min_vals[feat] = min(vals)
            max_vals[feat] = max(vals)

        for cand in candidates:
            cand.norm_features = {}
            for feat in features:
                raw_val = cand.raw_features[feat]
                denom = max_vals[feat] - min_vals[feat] + self.epsilon
                scaled = (raw_val - min_vals[feat]) / denom
                
                if feat == "delivery_risk":
                    # Invert risk so that HIGHER risk maps to a LOWER score (desirable / prioritized)
                    cand.norm_features[feat] = 1.0 - scaled
                else:
                    cand.norm_features[feat] = scaled
        
        # Wait, the architecture.md lists:
        # f_urg_hat as standard min-max?
        # Yes, Section 8.2: "For Distance, Waiting Time, and Delivery Risk: standard formula. For Urgency: standard formula. For Delivery Risk: 1.0 - standard formula."
        # This matches our implementation perfectly.
