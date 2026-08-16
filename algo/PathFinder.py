import heapq
from typing import List, Optional, Tuple, Set, Dict
from helpers.graph import GraphBuilder


class PathFinder:
    def __init__(self, graph: GraphBuilder) -> None:
        self.graph = graph
        self.paths: List[List[str]] = []
        self.blocked_edges: Set[Tuple[str, str]] = set()

    def count_path_cost(self, path: List[str]) -> float:
        """Total cost of a path (sum of movement costs to enter each zone)."""
        if len(path) <= 1:
            return 0

        total: float = 0
        for i in range(1, len(path)):
            zone_name = path[i]
            zone = self.graph.zones_dict[zone_name]
            if zone["zone"] == "restricted":
                total += 2
            else:
                total += 1

        return total

    def count_priority_zones(self, path: List[str]) -> int:
        """Total cost of a path (sum of movement costs to enter each zone)."""
        if len(path) <= 1:
            return 0

        total: int = 0
        for i in range(1, len(path)):
            zone_name = path[i]
            zone = self.graph.zones_dict[zone_name]
            if zone["zone"] == 'priority':
                total += 1
        return total

    def k_shortest_paths(
        self, start: str, end: str, K: int = 2
    ) -> List[List[str]]:
        """
        Returns up to K shortest paths from start to end, ordered by
        total cost.
        """

        def dijkstra_single(
            source: str,
            target: str,
            blocked_edges: Optional[Set[Tuple[str, str]]] = None
        ) -> Tuple[Optional[List[str]], float]:
            """
            Run Dijkstra from source to target.

            blocked_edges: set of (u, v) edges to exclude.
            Returns (path, cost) or (None, inf) if no path.
            """
            if blocked_edges is None:
                blocked_edges = set()

            dist: Dict[str, float] = {
                name: float("inf")
                for name in self.graph.zones_dict
            }
            parent: Dict[str, Optional[str]] = {
                name: None
                for name in self.graph.zones_dict
            }
            dist[source] = 0
            pq: List[Tuple[float, str]] = [(0, source)]

            while pq:
                current_cost, current_name = heapq.heappop(pq)

                if current_cost > dist[current_name]:
                    continue

                if current_name == target:
                    break

                current_zone = self.graph.zones_dict[current_name]

                for neighbor_zone, conn in current_zone["neighbors"]:
                    if neighbor_zone["zone"] == "blocked":
                        continue

                    if (
                        current_name,
                        neighbor_zone["name"],
                    ) in blocked_edges:
                        continue

                    if neighbor_zone["zone"] == "restricted":
                        move_cost = 2
                    elif neighbor_zone["zone"] == "priority":
                        move_cost = 1
                    else:
                        move_cost = 1

                    new_cost = current_cost + move_cost

                    if new_cost < dist[neighbor_zone["name"]]:
                        dist[neighbor_zone["name"]] = new_cost
                        parent[neighbor_zone["name"]] = current_name
                        heapq.heappush(
                            pq,
                            (new_cost, neighbor_zone["name"]),
                        )

            if dist[target] == float("inf"):
                return None, float("inf")

            path: List[str] = []
            cur: Optional[str] = target

            while cur is not None:
                path.append(cur)
                cur = parent[cur]

            path.reverse()
            return path, dist[target]

        final_paths: List[List[str]] = []
        candidate_paths: List[Tuple[float, List[str]]] = []

        first_path, first_cost = dijkstra_single(start, end)

        if not first_path:
            return []

        final_paths.append(first_path)

        for k in range(1, K):
            last_path = final_paths[-1]

            for i in range(len(last_path) - 1):
                spur_node = last_path[i]
                root_path = last_path[:i + 1]

                blocked_edges: Set[Tuple[str, str]] = set()

                for path in final_paths:
                    if (
                        len(path) > i
                        and path[:i + 1] == root_path
                    ):
                        blocked_edges.add(
                            (path[i], path[i + 1])
                        )

                def dijkstra_with_blocked_nodes(
                    source: str,
                    target: str,
                    blocked_edges: Set[Tuple[str, str]],
                    blocked_nodes: Set[str],
                ) -> Tuple[Optional[List[str]], float]:
                    """
                    Dijkstra that avoids blocked_edges and blocked_nodes.

                    blocked_nodes: set of node names that cannot be entered
                    (except source).
                    """
                    dist: Dict[str, float] = {
                        name: float("inf")
                        for name in self.graph.zones_dict
                    }
                    parent: Dict[str, Optional[str]] = {
                        name: None
                        for name in self.graph.zones_dict
                    }
                    dist[source] = 0.0
                    pq: List[Tuple[float, str]] = [(0.0, source)]

                    while pq:
                        current_cost, current_name = heapq.heappop(pq)

                        if current_cost > dist[current_name]:
                            continue

                        if current_name == target:
                            break

                        current_zone = self.graph.zones_dict[
                            current_name
                        ]

                        for neighbor_zone, conn in current_zone[
                            "neighbors"
                        ]:
                            if neighbor_zone["zone"] == "blocked":
                                continue

                            if (
                                current_name,
                                neighbor_zone["name"],
                            ) in blocked_edges:
                                continue

                            if neighbor_zone["name"] in blocked_nodes:
                                continue

                            if neighbor_zone["zone"] == "restricted":
                                move_cost = 2.0
                            elif neighbor_zone["zone"] == "priority":
                                move_cost = 0.9
                            else:
                                move_cost = 1.0

                            new_cost = current_cost + move_cost

                            if (
                                new_cost
                                < dist[neighbor_zone["name"]]
                            ):
                                dist[neighbor_zone["name"]] = new_cost
                                parent[
                                    neighbor_zone["name"]
                                ] = current_name
                                heapq.heappush(
                                    pq,
                                    (
                                        new_cost,
                                        neighbor_zone["name"],
                                    ),
                                )

                    if dist[target] == float("inf"):
                        return None, float("inf")

                    path: List[str] = []
                    cur: Optional[str] = target

                    while cur is not None:
                        path.append(cur)
                        cur = parent[cur]

                    path.reverse()
                    return path, dist[target]

                blocked_nodes = set(root_path[:-1])

                spur_path, spur_cost = (
                    dijkstra_with_blocked_nodes(
                        spur_node,
                        end,
                        blocked_edges,
                        blocked_nodes,
                    )
                )

                if spur_path is not None:
                    total_path = root_path[:-1] + spur_path
                    total_cost = spur_cost + self.count_path_cost(
                        root_path[:-1]
                    )
                    total_cost = self.count_path_cost(total_path)

                    if (
                        total_path not in final_paths
                        and total_path
                        not in [p for (c, p) in candidate_paths]
                    ):
                        heapq.heappush(
                            candidate_paths,
                            (total_cost, total_path),
                        )

            if not candidate_paths:
                break

            lowest_cost, best_path = heapq.heappop(
                candidate_paths
            )
            final_paths.append(best_path)

        if len(final_paths) > 1:
            print(final_paths)
            cost0 = self.count_path_cost(final_paths[0])
            cost1 = self.count_path_cost(final_paths[1])
            if cost0 == cost1:
                p1_priorities = self.count_priority_zones(final_paths[0])
                p2_priorities = self.count_priority_zones(final_paths[1])
                if p2_priorities > p1_priorities:
                    final_paths.reverse()

        return final_paths
