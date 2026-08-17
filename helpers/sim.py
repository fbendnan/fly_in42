from typing import (
    Dict,
    List,
    Any,
    Optional,
    Tuple,
    DefaultDict,
)
from collections import defaultdict

from helpers.dron import Drone
from algo.PathFinder import PathFinder
from helpers.graph import GraphBuilder


class Simulation:
    def __init__(
        self,
        graph: GraphBuilder,
        nb_drones: int
    ) -> None:

        self.graph: GraphBuilder = graph
        self.nb_drones: int = nb_drones

        assert graph.data is not None
        assert graph.data.start_hub is not None
        assert graph.data.end_hub is not None

        self.start: str = graph.data.start_hub["name"]
        self.end: str = graph.data.end_hub["name"]

        self.zones_dict: Dict[str, Any] = graph.zones_dict

        self.turns: int = 0
        self.drones: List[Drone] = []

        self.zone_occupancy: Dict[str, List[int]] = {
            name: [] for name in self.zones_dict
        }
        self.conn_occupancy: DefaultDict[
            Tuple[str, str], int
        ] = defaultdict(int)
        self.drone_connections: Dict[
            int, Tuple[str, str]
        ] = {}
        self.reserved_for_restricted: DefaultDict[
            str, int
        ] = defaultdict(int)

        self._create_drones()

        self.zone_occupancy[self.start] = list(
            range(1, nb_drones + 1)
        )

    def _create_drones(self) -> None:
        pf = PathFinder(self.graph)

        paths = pf.k_shortest_paths(
            self.start,
            self.end
        )

        if not paths:
            raise ValueError(
                "No path from start to end zone"
            )

        for i in range(self.nb_drones):

            path = paths[i % len(paths)]

            drone = Drone(
                i + 1,
                self.start
            )

            drone.path = path.copy()

            self.drones.append(drone)

    def _all_delivered(self) -> bool:
        """Return True if all drones are delivered."""

        return all(
            drone.state == "delivered"
            for drone in self.drones
        )

    def _get_connection(
        self,
        curr_zone: str,
        next_zone: str
    ) -> Optional[Dict[str, Any]]:

        """
        Find the connection object between two zones.

        This retrieves the connection metadata, for example:

            {
                "zone1": "A",
                "zone2": "B",
                "max_link_capacity": 2
            }
        """

        assert self.graph.data is not None

        for conn in self.graph.data.connections:

            if (
                conn["zone1"] == curr_zone
                and conn["zone2"] == next_zone
            ) or (
                conn["zone1"] == next_zone
                and conn["zone2"] == curr_zone
            ):
                return dict(conn)

        return None

    def _connection_key(
        self,
        zone1: str,
        zone2: str
    ) -> Tuple[str, str]:

        """
        Create a unique key for a bidirectional connection.

        A -> B and B -> A produce the same key.
        """

        return (
            min(zone1, zone2),
            max(zone1, zone2)
        )
    def _zone_available_space(self) -> Dict[str, int]:
        """
        Return the number of free spaces in each zone.

        Normal zone:

            max_drones
            - drones currently inside
            - reserved spaces

        Start and end hubs have unlimited capacity.
        """

        available: Dict[str, int] = {}

        for name, zone_obj in self.zones_dict.items():

            if name == self.start or name == self.end:
                available[name] = float("inf")
                continue

            occupied = len(
                self.zone_occupancy[name]
            )

            reserved = self.reserved_for_restricted.get(
                name,
                0
            )

            available[name] = (
                zone_obj["max_drones"]
                - occupied
                - reserved
            )

        return available

    def _connection_has_space(
        self,
        conn_key: Tuple[str, str],
        max_capacity: int,
        entering_this_turn: int
    ) -> bool:

        """
        Check whether drones can enter the connection.

        We count:

            drones already in the connection
            +
            drones accepted during this turn

        against max_link_capacity.
        """

        current_occupancy = self.conn_occupancy[
            conn_key
        ]

        total = current_occupancy + entering_this_turn

        return total < max_capacity

    def step(self) -> bool:
        """
        Execute one simulation turn.

        Return True when all drones are delivered.
        """

        if self._all_delivered():
            return True

        turn_moves: List[str] = []

        arriving_drones: List[Drone] = [
            drone
            for drone in self.drones
            if drone.state == "in_transit"
        ]

        for drone in arriving_drones:

            to_zone = drone.target_zone
            assert to_zone is not None

            conn_key = self.drone_connections.pop(
                drone.id,
                None
            )

            if conn_key is not None:

                self.conn_occupancy[conn_key] -= 1

                if self.conn_occupancy[conn_key] == 0:
                    del self.conn_occupancy[conn_key]

            self.zone_occupancy[to_zone].append(drone.id)

            drone.current_zone = to_zone
            drone.target_zone = None
            drone.state = "in_zone"

            turn_moves.append(f"D{drone.id}-{to_zone}")

            if self.reserved_for_restricted.get(to_zone, 0) > 0:

                self.reserved_for_restricted[to_zone] -= 1

                if self.reserved_for_restricted[to_zone] == 0:
                    del self.reserved_for_restricted[to_zone]

            if to_zone == self.end:

                drone.state = "delivered"

                self.zone_occupancy[to_zone].remove(drone.id)

        proposals: List[
            Tuple[
                Drone,
                str,
                str,
                Dict[str, Any]
            ]
        ] = []

        for drone in self.drones:

            if drone.state != "in_zone":
                continue

            if len(drone.path) <= 1:

                if drone.current_zone == self.end:
                    drone.state = "delivered"

                    if drone.id in self.zone_occupancy[
                        drone.current_zone
                    ]:
                        self.zone_occupancy[
                            drone.current_zone
                        ].remove(drone.id)

                continue

            next_zone = drone.path[1]

            conn = self._get_connection(
                drone.current_zone,
                next_zone
            )

            if conn is None:
                continue

            proposals.append(
                (
                    drone,
                    drone.current_zone,
                    next_zone,
                    conn
                )
            )

        zone_availability = self._zone_available_space()

        proposals.sort(
            key=lambda proposal: (
                len(proposal[0].path),
                proposal[0].id
            )
        )

        accepted_connections: DefaultDict[
            Tuple[str, str],
            int
        ] = defaultdict(int)

        accepted_proposals: List[
            Tuple[
                Drone,
                str,
                str,
                Dict[str, Any]
            ]
        ] = []

        for (
            drone,
            from_zone,
            to_zone,
            conn
        ) in proposals:

            if drone.id not in self.zone_occupancy[from_zone]:
                continue

            conn_key = self._connection_key(
                from_zone,
                to_zone
            )

            if not self._connection_has_space(
                conn_key,
                conn["max_link_capacity"],
                accepted_connections[conn_key]
            ):
                continue

            if zone_availability[to_zone] <= 0:
                continue

            accepted_proposals.append(
                (
                    drone,
                    from_zone,
                    to_zone,
                    conn
                )
            )

            accepted_connections[conn_key] += 1

            zone_availability[to_zone] -= 1
            zone_availability[from_zone] += 1

        for (
            drone,
            from_zone,
            to_zone,
            conn
        ) in accepted_proposals:

            self.zone_occupancy[from_zone].remove(
                drone.id
            )

            conn_name = f"{conn['zone1']}-{conn['zone2']}"

            destination = self.zones_dict[to_zone]

            if destination["zone"] == "restricted":

                drone.state = "in_transit"
                drone.target_zone = to_zone

                self.reserved_for_restricted[to_zone] += 1

                conn_key = self._connection_key(
                    from_zone,
                    to_zone
                )

                self.conn_occupancy[conn_key] += 1

                self.drone_connections[drone.id] = conn_key

                turn_moves.append(
                    f"D{drone.id}-{conn_name}"
                )

            else:

                drone.current_zone = to_zone

                self.zone_occupancy[to_zone].append(drone.id)

                turn_moves.append(
                    f"D{drone.id}-{to_zone}"
                )

                if to_zone == self.end:

                    drone.state = "delivered"

                    self.zone_occupancy[to_zone].remove(drone.id)

            if (
                drone.path
                and drone.path[0] == from_zone
            ):
                drone.path.pop(0)

        if turn_moves:
            print(" ".join(turn_moves))

        self.turns += 1

        return self._all_delivered()
