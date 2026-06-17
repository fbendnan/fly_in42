from dron import Drone
from algo.PathFinder import PathFinder
from collections import defaultdict


class Simulation:
    def __init__(self, graph, nb_drones):
        self.graph = graph
        self.nb_drones = nb_drones
        self.start = graph.data.start_hub.name
        self.end = graph.data.end_hub.name
        self.zones = graph.zones_dict
        self.turns = 0
        self.drones = []
        self.zone_occupancy = {name: [] for name in self.zones}
        self._create_drones()
        self.zone_occupancy[self.start] = list(range(1, nb_drones + 1))


    def _create_drones(self):
        pf = PathFinder(self.graph)
        best_path = pf.dijkstra()
        if not best_path:
            raise ValueError("No path from start to end zone")
        for i in range(1, self.nb_drones + 1):
            drone = Drone(i, self.start)
            drone.path = best_path.copy()
            self.drones.append(drone)

    def _all_delivered(self):
        return all(d.state == "delivered" for d in self.drones)
    
    def _get_connection(self, curr_zone, next_zone):
        for conn in self.graph.data.connections:
            if (conn.zone1 == curr_zone and conn.zone2 == next_zone) or \
               (conn.zone1 == next_zone and conn.zone2 == curr_zone):
                return conn
        return None

    def step(self):
        if self._all_delivered():
            return True

        turn_moves = []
        proposals = [] #(drone, from_z, to_z, conn)
        for drone in self.drones:
            if drone.state != "in_zone":
                continue
            if len(drone.path) <= 1:
                if drone.current_zone == self.end:
                    drone.state = "delivered"
                continue
            next_zone = drone.path[1]
            conn = self._get_connection(drone.current_zone, next_zone)
            if not conn:
                continue
            proposals.append((drone, drone.current_zone, next_zone, conn))  

        #we should see the conn capacity and the zone capacity (filter proposals)
        proposals_by_dest = defaultdict(list)
        #ch7al mn zone baghya tmchi l kol zone
        for p in proposals:
            to_zone = p[2]
            proposals_by_dest[to_zone].append(p)

        accepted_proposals = []
        accepted_connections = defaultdict(int) #to check the number of drones that can travel through this conn
    
        leaving_zone_count = defaultdict(int)
        for (drone, from_z, to_z, conn) in proposals:
            leaving_zone_count[from_z] += 1

        for to_zone, plist in proposals_by_dest.items():
            if to_z == self.end:
                for p in plist:
                    drone, from_z, to_z, conn = p
                    connection = tuple(sorted([from_z, to_z]))
                    if accepted_connections[connection] >= conn.max_link_capacity:
                        continue
                    accepted_proposals.append(p)
                    accepted_connections[connection] += 1
                continue

            nb_drones_occup_to_z = len(self.zone_occupancy[to_zone])
            nb_drones_leaving_to_z = leaving_zone_count[to_zone]
            available_place_at_to_z = self.zones[to_zone].max_drones - (nb_drones_occup_to_z - nb_drones_leaving_to_z)
            if available_place_at_to_z <= 0:
                continue
            plist.sort(key=lambda p: p[0].id)
            accepted = 0
            for p in plist:
                if accepted >= available_place_at_to_z:
                    break
                drone, from_z, to_z, conn  = p
                connection = tuple(sorted([from_z, to_z]))
                if accepted_connections[connection] >= conn.max_link_capacity:
                    continue
                accepted_proposals.append(p)
                accepted_connections[connection] += 1
                accepted += 1

        for (drone, from_z, to_z, conn) in accepted_proposals:
            self.zone_occupancy[from_z].remove(drone.id)
            drone.current_zone = to_z
            self.zone_occupancy[to_z].append(drone.id)
            turn_moves.append(f"D{drone.id}-{to_z}")
            if drone.path and drone.path[0] == from_z:
                drone.path.pop(0)
            if to_z == self.end:
                drone.state = "delivered"
        
        if turn_moves:
            print(" ".join(turn_moves))
        
        self.turns += 1
        return self._all_delivered()