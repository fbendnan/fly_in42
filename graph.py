from zone import Zone
from parse.parsing import ParseConfig
import heapq


class Graph:
    def __init__(self, file_name):
        self.data = None
        self.zones_dict = {}
        self.file_name = file_name

    def build(self):
        self.data = ParseConfig(self.file_name)
        self.data.parser()
        self.zones_dict[self.data.start_hub.name] = self.data.start_hub
        print("this is data from build fun :", self.data.start_hub)
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
        dist = {name: float('inf') for name in self.zones_dict.keys()}
        dist[self.data.start_hub.name] = 0
        prev = {}
        pq = [(0, self.data.start_hub.name)]

        while pq:
            current_cost, current_name = heapq.heappop(pq)
            print(current_name)

            if current_name == self.data.end_hub.name:
                break

            if current_cost > dist[current_name]:
                continue

            current_zone = self.zones_dict[current_name]

            for neighbor_zone, conn in current_zone.neighbors:
                if neighbor_zone.zone == 'blocked':
                    continue

                if neighbor_zone.zone == 'priority':
                    cost = 1
                elif neighbor_zone.zone == 'normal':
                    cost = 2
                else:
                    cost = 3
                new_cost = current_cost + cost

                if new_cost < dist[neighbor_zone.name]:
                    dist[neighbor_zone.name] = new_cost
                    prev[neighbor_zone.name] = current_zone
                    heapq.heappush(pq, (new_cost, neighbor_zone.name))

        path = []
        curr = self.zones_dict.get(self.data.end_hub.name)
        while curr is not None:
            path.append(curr.name)
            curr = prev.get(curr.name)

        path.reverse()
        return path

            

# 1-  every zone should know their neighbors
# 2 - 


#handle the acceptation of the negative value in the graph cordinat(should be acceptable)