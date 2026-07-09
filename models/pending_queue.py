from typing import Set, List

class PendingQueue:
    def __init__(self, initial_customer_ids: Set[str]):
        self._unserved: Set[str] = set(initial_customer_ids)

    def remove(self, customer_id: str) -> None:
        if customer_id in self._unserved:
            self._unserved.remove(customer_id)

    def get_pending(self) -> Set[str]:
        return set(self._unserved)

    def get_all_pending(self) -> List[str]:
        return list(self._unserved)

    def is_empty(self) -> bool:
        return len(self._unserved) == 0

    def get_unserved_count(self) -> int:
        return len(self._unserved)
