from zone import Zone
from parse.parsing import ParseConfig


class Graph:
    def __init__(self, file_name):
        self.data = None
        self.zones_dict = {}
        self.file_name = file_name

    def build(self):
        self.data = ParseConfig(self.file_name)
        self.data.parser()
        self.zones_dict[self.data.start_hub.name] = self.data.start_hub
        print("this id data from buikd fiun::", self.data)
        self.zones_dict[self.data.end_hub.name] = self.data.end_hub
        for hub in self.data.hubs:
            self.zones_dict[hub.name] = hub

    def add_zone_neighbors(self):
        for conn in self.data.connections:
            z1 = self.zones_dict[conn.zone1]
            z2 = self.zones_dict[conn.zone2]

            z1.neighbors.append((z2, conn))
            z2.neighbors.append((z1, conn))

    def djikstra(self):
        current = self.zones_dict.get("start")
        # print(self.zones_dict)
        print(current)


# 1-  every zone should know their neighbors
# 2 - 
