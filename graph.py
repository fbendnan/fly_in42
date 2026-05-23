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
        path = []
        total_cost = 0
        current = self.zones_dict.get("start")
        path.append(current.name)
        print(current.neighbors)
        z, c = current.neighbors[0]
        choosen = self.zones_dict.get(z.name)
        while(current.name != self.data.end_hub.name):
            for x, y in current.neighbors:
                if x.zone == 'perfect':
                    choosen = self.zones_dict.get(x.name)
                    total_cost += 1

                elif x.zone == 'normal' and choosen.zone != 'perfect':
                    choosen = self.zones_dict.get(x.name)
                    total_cost += 1

                elif x.zone == 'restricted' and choosen.zone != 'perfect' and choosen.zone != 'normal':
                    choosen = self.zones_dict.get(x.name)
                    total_cost += 2
                
                elif x.zone == 'blocked':
                    choosen = None
            current  = choosen
            path.append(current.name)

        return path

            

# 1-  every zone should know their neighbors
# 2 - 


#handle the acceptation of the negative value in the graph cordinat(should be acceptable)