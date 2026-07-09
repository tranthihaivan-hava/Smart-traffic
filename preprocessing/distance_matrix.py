import math
from typing import List, Dict
from models.customer import Customer

class DistanceMatrix:
    def __init__(self, customers: List[Customer], depot: Customer):
        self.nodes = {depot.id: depot}
        for c in customers:
            self.nodes[c.id] = c
        self.matrix: Dict[str, Dict[str, float]] = {}
        self._compute_matrix()

    def _compute_matrix(self):
        for id1, node1 in self.nodes.items():
            self.matrix[id1] = {}
            for id2, node2 in self.nodes.items():
                dist = math.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)
                self.matrix[id1][id2] = dist

    def get_distance(self, from_id: str, to_id: str) -> float:
        return self.matrix[from_id][to_id]

    def get_matrix(self) -> List[List[float]]:
        # Returns raw matrix in list form sorted by keys
        sorted_keys = sorted(self.nodes.keys())
        return [[self.matrix[k1][k2] for k2 in sorted_keys] for k1 in sorted_keys]
