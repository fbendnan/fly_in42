from zone import Zone
from parser.parsing import ParseConfig


class Graph:
    def __init__(self, file_name):
        self.data = None
        self.zones = []
        self.file_name = file_name

    def add_zone(self):
        self.data = ParseConfig(self.file_name)
        
        self.zones.append(Zone(self.data.start_hub.name, self.data.start_hub.x, self.data.start_hub.y))
        # print(self.data.start_hub["name"])