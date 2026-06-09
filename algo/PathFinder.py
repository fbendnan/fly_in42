import heapq

class PathFinder:
    def __init__(self, graph):
        self.graph = graph
        self.paths = []
        self.blocked_edges = set()
    

    def dijkstra(self):
        start = self.graph.data.start_hub.name
        end = self.graph.data.end_hub.name

        dist = {name: float("inf") for name in self.graph.zones_dict}
        dist[start] = 0

        best_priority = {name: -1 for name in self.graph.zones_dict}
        best_priority[start] = 0

        prev = {}
        pq = [(0, 0, start)]  # (cost, -priority, name)

        while pq:
            current_cost, neg_priority, current_name = heapq.heappop(pq)
            current_priority = -neg_priority
            print(current_priority)
            if current_name == end:
                break

            if current_cost > dist[current_name] or (
                current_cost == dist[current_name]
                and current_priority < best_priority[current_name]
            ):
                continue

            current_zone = self.graph.zones_dict[current_name]

            for neighbor_zone, conn in current_zone.neighbors:
                if neighbor_zone.zone == "blocked":
                    continue

                if neighbor_zone.zone == "restricted":
                    move_cost = 2
                else:
                    move_cost = 1

                new_cost = current_cost + move_cost

                new_priority = current_priority + (
                    1 if neighbor_zone.zone == "priority" else 0
                )

                if new_cost < dist[neighbor_zone.name] or (
                    new_cost == dist[neighbor_zone.name]
                    and new_priority > best_priority[neighbor_zone.name]
                ):
                    dist[neighbor_zone.name] = new_cost
                    best_priority[neighbor_zone.name] = new_priority
                    prev[neighbor_zone.name] = current_zone
                    heapq.heappush(pq, (new_cost, -new_priority, neighbor_zone.name))
        
                
        path = []
        curr = self.graph.zones_dict.get(end)
        while curr is not None:
            path.append(curr.name)
            curr = prev.get(curr.name)
        path.reverse()

        return path if path and path[0] == start else []
