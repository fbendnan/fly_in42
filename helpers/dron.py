from typing import List, Optional


class Drone:
    def __init__(self, drone_id: int, start_zone: str) -> None:
        self.id: int = drone_id
        self.path: List[str] = []
        self.current_zone: str = start_zone
        self.state: str = "in_zone"
        self.target_zone: Optional[str] = None
