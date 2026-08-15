import heapq

class PathFinder:
    def __init__(self, graph):
        self.graph = graph
        self.paths = []
        self.blocked_edges = set()
    
    def count_path_cost(self, path):
        """Total cost of a path (sum of movement costs to enter each zone)."""
        if len(path) <= 1:
            return 0
        total = 0
        for i in range(1, len(path)):
            zone_name = path[i]
            zone = self.graph.zones_dict[zone_name]
            if zone.zone == "restricted":
                total += 2
            else:
                total += 1
        return total

    def k_shortest_paths(self, start, end, K=2):
        """
        Returns up to K shortest paths from start to end, ordered by total cost.
        """    
        def dijkstra_single(source, target, blocked_edges=None):
            """
            Run Dijkstra from source to target.
            blocked_edges: set of (u, v) edges to exclude.
            Returns (path, cost) or (None, inf) if no path.
            """
            if blocked_edges is None:
                blocked_edges = set()

            dist = {name: float('inf') for name in self.graph.zones_dict}
            parent = {name: None for name in self.graph.zones_dict}
            dist[source] = 0
            pq = [(0, source)]

            while pq:
                current_cost, current_name = heapq.heappop(pq)
                if current_cost > dist[current_name]:
                    continue
                if current_name == target:
                    break
                current_zone = self.graph.zones_dict[current_name]
                
                for neighbor_zone, conn in current_zone.neighbors:
                    if neighbor_zone.zone == "blocked":
                        continue
                    if (current_name, neighbor_zone.name) in blocked_edges:
                        continue
                    if neighbor_zone.zone == "restricted":
                        move_cost = 2
                    elif neighbor_zone.zone == "priority":
                        move_cost = 0.9
                    else:
                        move_cost = 1
                    # move_cost = 2 if neighbor_zone.zone == "restricted" else 1
                    new_cost = current_cost + move_cost
                    if new_cost < dist[neighbor_zone.name]:
                        dist[neighbor_zone.name] = new_cost
                        parent[neighbor_zone.name] = current_name
                        heapq.heappush(pq, (new_cost, neighbor_zone.name))

            if dist[target] == float('inf'):
                return None, float('inf')

            path = []
            cur = target
            while cur is not None:
                path.append(cur)
                cur = parent[cur]
            path.reverse()
            return path, dist[target]

        final_paths = []
        candidate_paths = []

        first_path, first_cost = dijkstra_single(start, end)
        if not first_path:
            return []

        final_paths.append(first_path)

        for k in range(1, K):
            last_path = final_paths[-1]
            for i in range(len(last_path) - 1):
                spur_node = last_path[i]
                root_path = last_path[:i+1]

                blocked_edges = set()
                for path in final_paths:
                    if len(path) > i and path[:i+1] == root_path:
                        blocked_edges.add((path[i], path[i+1]))

                def dijkstra_with_blocked_nodes(source, target, blocked_edges, blocked_nodes):
                    """
                    Dijkstra that avoids blocked_edges and blocked_nodes.
                    blocked_nodes: set of node names that cannot be entered (except source).
                    """
                    dist = {name: float('inf') for name in self.graph.zones_dict}
                    parent = {name: None for name in self.graph.zones_dict}
                    dist[source] = 0
                    pq = [(0, source)]

                    while pq:
                        current_cost, current_name = heapq.heappop(pq)
                        if current_cost > dist[current_name]:
                            continue
                        if current_name == target:
                            break
                        current_zone = self.graph.zones_dict[current_name]
                        for neighbor_zone, conn in current_zone.neighbors:
                            if neighbor_zone.zone == "blocked":
                                continue
                            if (current_name, neighbor_zone.name) in blocked_edges:
                                continue
                            if neighbor_zone.name in blocked_nodes:
                                continue
                            # move_cost = 2 if neighbor_zone.zone == "restricted" else 1
                            if neighbor_zone.zone == "restricted":
                                move_cost = 2
                            elif neighbor_zone.zone == "priority":
                                move_cost = 0.9
                            else:
                                move_cost = 1
                            new_cost = current_cost + move_cost
                            if new_cost < dist[neighbor_zone.name]:
                                dist[neighbor_zone.name] = new_cost
                                parent[neighbor_zone.name] = current_name
                                heapq.heappush(pq, (new_cost, neighbor_zone.name))

                    if dist[target] == float('inf'):
                        return None, float('inf')

                    path = []
                    cur = target
                    while cur is not None:
                        path.append(cur)
                        cur = parent[cur]
                    path.reverse()
                    return path, dist[target]

                blocked_nodes = set(root_path[:-1])

                spur_path, spur_cost = dijkstra_with_blocked_nodes(
                    spur_node, end, blocked_edges, blocked_nodes
                )

                if spur_path is not None:
                    total_path = root_path[:-1] + spur_path
                    total_cost = spur_cost + self.count_path_cost(root_path[:-1])
                    total_cost = self.count_path_cost(total_path)
                    if total_path not in [p for p in final_paths] and total_path not in [p for (c,p) in candidate_paths]:
                        heapq.heappush(candidate_paths, (total_cost, total_path))

            if not candidate_paths:
                break

            lowest_cost, best_path = heapq.heappop(candidate_paths)
            final_paths.append(best_path)

        return final_paths
