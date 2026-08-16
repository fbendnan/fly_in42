from typing import Any, Optional
from parse.parsing import ParseConfig


class GraphBuilder:
    def __init__(self, file_name: str) -> None:
        self.data: Optional[ParseConfig] = None
        self.zones_dict: dict[str, Any] = {}
        self.file_name: str = file_name
        self.drones: list[Any] = []

    def build(self) -> None:
        self.data = ParseConfig(self.file_name)
        assert self.data is not None
        self.data.parser()
        assert self.data.start_hub is not None
        assert self.data.end_hub is not None
        self.zones_dict[self.data.start_hub["name"]] = self.data.start_hub
        self.zones_dict[self.data.end_hub["name"]] = self.data.end_hub
        for hub in self.data.hubs:
            self.zones_dict[hub["name"]] = hub

    def add_zone_neighbors(self) -> None:
        assert self.data is not None
        for conn in self.data.connections:
            z1 = self.zones_dict[conn["zone1"]]
            z2 = self.zones_dict[conn["zone2"]]
            z1["neighbors"].append((z2, conn))
            z2["neighbors"].append((z1, conn))
    # def add_costs(self):
    #     for key, zone in self.zones_dict.items():
    #         if zone["zone"]== 'blocked':
    #             continue
    #         if zone["zone"]== 'restricted':
    #             zone.cost = 2
    #         else:
    #             zone.cost = 1
