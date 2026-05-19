from zone import Zone
from parse.parsing import ParseConfig


class Graph:
    def __init__(self, file_name):
        self.data = None
        self.zones = []
        self.file_name = file_name

    def add_zone(self):
        self.data = ParseConfig(self.file_name)
        self.data.parser()
        self.zones.append(self.data.start_hub)
        self.zones.append(self.data.end_hub)
        for hub in self.data.hubs:
            self.zones.append(hub)


#if