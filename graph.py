from parse.parsing import ParseConfig
from algo.PathFinder import PathFinder


class GraphBuilder:
    def __init__(self, file_name):
        self.data = None
        self.zones_dict = {}
        self.file_name = file_name

    def build(self):
        self.data = ParseConfig(self.file_name)
        self.data.parser()
        self.zones_dict[self.data.start_hub.name] = self.data.start_hub
        self.zones_dict[self.data.end_hub.name] = self.data.end_hub
        for hub in self.data.hubs:
            self.zones_dict[hub.name] = hub

    def add_zone_neighbors(self):
        for conn in self.data.connections:
            z1 = self.zones_dict[conn.zone1]
            z2 = self.zones_dict[conn.zone2]

            z1.neighbors.append((z2, conn))
            z2.neighbors.append((z1, conn))

    def add_costs(self):
        for key, zone in self.zones_dict.items():
            if zone.zone == 'blocked':
                continue
            if zone.zone == 'restricted':
                zone.cost = 2
            else:
                zone.cost = 1



    def get_all_shortest_paths_from(self, start_name):
        """Return a list of all shortest paths (by cost) from start_name to end."""
        from algo.PathFinder import PathFinder
        pf = PathFinder(self)
        # You need to modify PathFinder.dijkstra to return distance map and predecessor map
        # Then use backtracking to find all paths (as shown earlier)
        # For simplicity, return a single path for now.
        return [pf.dijkstra_from(start_name)]   # you must implement dijkstra_from


# 1-  every zone should know their neighbors
# 2 -


# handle the acceptation of the negative value in the graph cordinat(should be acceptable)
