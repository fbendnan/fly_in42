from parser.hub_model import HubModel

class ParseConfig():
    def __init__(self, file_name):
        self.file_name = file_name
        self.nb_drones = 0
        self.start_hub = None
        self.end_hub = None
        self.hubs = []
        self.connections = []

    

    def parser(self):
        mandatories = ["nb_drones", "start_hub", "end_hub", "hub", "connection"]
        config = {}
        with open(self.file_name) as f:
            i = 0
            for l in f:
                if not l or l.startswith('#'):
                    continue
                i += 1
                l = l.split(':')
                l[0] = l[0].strip()
                if i == 1 and (l[0] != "nb_drones" or len(l) != 2 or int(l[1].strip()) < 1):
                    raise ValueError(
                        "the first line should have the nb_drones : n > 1")
                if l[0] == "nb_drones":
                    config["nb_drones"] = int(l[1].strip())
                if l[0] == "start_hub":
                    HubModel.validate_hub(l[1].strip())
                if l[0] == "end_hub":
                    ...
                if l[0] == "hub":
                    ...
                if l[0] == "connection":
                    ...
                
        return config
