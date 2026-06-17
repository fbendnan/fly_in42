from typing import List

class Drone:
    def __init__(self, drone_id: int, start_zone: str):
        self.id = drone_id
        self.path: List[str] = []
        self.current_zone: any = start_zone
        self.state: str = "in_zone" #("in_conn", "delivered")