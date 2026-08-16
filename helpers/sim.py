from typing import Dict, List, Any, Optional, Tuple, DefaultDict
from helpers.dron import Drone
from algo.PathFinder import PathFinder
from collections import defaultdict
from helpers.graph import GraphBuilder


class Simulation:
    def __init__(self, graph: GraphBuilder, nb_drones: int) -> None:
        self.graph: GraphBuilder = graph
        self.nb_drones: int = nb_drones
        self.start: str = graph.data.start_hub["name"]
        self.end: str = graph.data.end_hub["name"]
        self.zones: Dict[str, Any] = graph.zones_dict
        self.turns: int = 0
        self.drones: List[Drone] = []
        self.zone_occupancy: Dict[str, List[int]] = {
            name: [] for name in self.zones}
        self.conn_occupency: DefaultDict[Any, int] = defaultdict(int)
        self.reserved: DefaultDict[Any, int] = defaultdict(int)
        self._create_drones()
        self.zone_occupancy[self.start] = list(range(1, nb_drones + 1))

    def _create_drones(self) -> None:
        pf = PathFinder(self.graph)
        paths = pf.k_shortest_paths(self.start, self.end)
        if not paths:
            raise ValueError("No path from start to end zone")
        for i in range(self.nb_drones):
            path = paths[i % len(paths)]
            drone = Drone(i + 1, self.start)
            drone.path = path.copy()
            self.drones.append(drone)

    def _all_delivered(self) -> bool:
        return all(d.state == "delivered" for d in self.drones)

    def _get_connection(
        self, curr_zone: str, next_zone: str
    ) -> Optional[Dict[str, Any]]:
        for conn in self.graph.data.connections:
            if (
                conn["zone1"] == curr_zone
                and conn["zone2"] == next_zone
            ) or (
                conn["zone1"] == next_zone
                and conn["zone2"] == curr_zone
            ):
                return conn
        return None

    def _zone_available_space(self) -> Dict[str, int]:
        """
        Returns a dict {zone_name: free_slots}.
        free_slots = max_drones - (drones currently inside)
        - (drones in transit TO this zone)
        """
        avail: Dict[str, int] = {}
        for name, zone_obj in self.zones.items():
            occupied = len(self.zone_occupancy[name])
            reserved = self.reserved.get(name, 0)
            avail[name] = (
                zone_obj["max_drones"] - occupied - reserved
            )
        return avail

    def step(self) -> bool:
        if self._all_delivered():
            return True

        turn_moves: List[str] = []
        arriving_drones: List[Drone] = [
            d for d in self.drones if d.state == "in_transit"
        ]
        proposals: List[Tuple[Drone, str, str, Dict[str, Any]]] = []

        for drone in self.drones:
            if drone.state != "in_zone":
                continue

            if len(drone.path) <= 1:
                if (
                    drone.current_zone == self.end
                    and drone.state != "delivered"
                ):
                    drone.state = "delivered"
                    if drone.id in self.zone_occupancy[
                        drone.current_zone
                    ]:
                        self.zone_occupancy[
                            drone.current_zone
                        ].remove(drone.id)
                continue

            nxt = drone.path[1]
            conn = self._get_connection(drone.current_zone, nxt)
            if not conn:
                continue
            proposals.append(
                (drone, drone.current_zone, nxt, conn)
            )

        available = self._zone_available_space()

        proposals.sort(
            key=lambda p: (len(p[0].path), p[0].id)
        )

        accepted_proposals: List[Tuple[Drone, str, str, Dict[str, Any]]] = []
        accepted_connections: DefaultDict[
            Tuple[str, str], int] = defaultdict(int)

        for drone, from_z, to_z, conn in proposals:
            if drone.id not in self.zone_occupancy[from_z]:
                continue

            conn_key = tuple(sorted([from_z, to_z]))

            if (
                accepted_connections[conn_key]
                >= conn["max_link_capacity"]
            ):
                continue

            if available[to_z] <= 0:
                continue

            accepted_proposals.append(
                (drone, from_z, to_z, conn)
            )
            accepted_connections[conn_key] += 1
            available[to_z] -= 1
            available[from_z] += 1

        for drone, from_z, to_z, conn in accepted_proposals:
            self.zone_occupancy[from_z].remove(drone.id)
            conn_name = f"{conn['zone1']}-{conn['zone2']}"

            zone_obj = self.zones[to_z]

            if zone_obj["zone"] == "restricted":
                drone.state = "in_transit"
                drone.target_zone = to_z
                self.reserved[to_z] += 1
                turn_moves.append(
                    f"D{drone.id}-{conn_name}"
                )

                if drone.path and drone.path[0] == from_z:
                    drone.path.pop(0)
            else:
                drone.current_zone = to_z
                self.zone_occupancy[to_z].append(drone.id)
                turn_moves.append(f"D{drone.id}-{to_z}")

                if drone.path and drone.path[0] == from_z:
                    drone.path.pop(0)

                if to_z == self.end:
                    drone.state = "delivered"
                    self.zone_occupancy[to_z].remove(drone.id)

        for drone in arriving_drones:
            to_zone = drone.target_zone

            turn_moves.append(f"D{drone.id}-{to_zone}")
            self.zone_occupancy[to_zone].append(drone.id)
            drone.state = "in_zone"
            drone.current_zone = to_zone
            drone.target_zone = None

            if to_zone == self.end:
                drone.state = "delivered"
                self.zone_occupancy[to_zone].remove(drone.id)

            if (
                to_zone in self.reserved
                and self.reserved[to_zone] > 0
            ):
                self.reserved[to_zone] -= 1
                if self.reserved[to_zone] == 0:
                    del self.reserved[to_zone]

        if turn_moves:
            print(" ".join(turn_moves))

        self.turns += 1
        return self._all_delivered()
