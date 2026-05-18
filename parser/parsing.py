from parser.hub_model import HubModel
from parser.connection import Connection

class ParseConfig:
    def __init__(self, file_name: str):
        self.file_name = file_name
        self.nb_drones = 0
        self.start_hub = None
        self.end_hub = None
        self.hubs = []
        self.connections = []

    def parser(self):
        with open(self.file_name) as f:
            lines = f.readlines()

        line_no = 0
        for raw_line in lines:
            stripped = raw_line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            line_no += 1
            parts = stripped.split(':', 1)
            if len(parts) != 2:
                raise ValueError(f"Line {line_no}: Missing colon separator")
            key = parts[0].strip()
            value = parts[1].strip()
            if line_no == 1:
                if key != "nb_drones":
                    raise ValueError(f"Line {line_no}: First line must be 'nb_drones'")
                try:
                    self.nb_drones = int(value)
                except ValueError:
                    raise ValueError(f"Line {line_no}: nb_drones must be integer, got '{value}'")
                if self.nb_drones < 1:
                    raise ValueError(f"Line {line_no}: nb_drones must be ≥ 1, got {self.nb_drones}")
                continue

            try:
                if key == "start_hub":
                    validated_data = HubModel.validate_hub(value)
                    self.start_hub = HubModel(**validated_data)
                elif key == "end_hub":
                    validated_data = HubModel.validate_hub(value)
                    self.end_hub = HubModel(**validated_data)
                elif key == "hub":
                    validated_data = HubModel.validate_hub(value)
                    self.hubs.append(HubModel(**validated_data))
                elif key == "connection":
                    validated_data = Connection.validate_connection(value)
                    self.connections.append(Connection(**validated_data))
                else:
                    raise ValueError(f"Unknown keyword '{key}'")
            except Exception as e:
                raise ValueError(f"Line {line_no}: {e}")

        if self.start_hub is None:
            raise ValueError("Missing 'start_hub' definition")
        if self.end_hub is None:
            raise ValueError("Missing 'end_hub' definition")

        all_zone_names = {self.start_hub.name, self.end_hub.name}
        all_zone_names.update(hub.name for hub in self.hubs)

        for conn in self.connections:
            if conn.zone1 not in all_zone_names:
                raise ValueError(f"Connection references unknown zone '{conn.zone1}'")
            if conn.zone2 not in all_zone_names:
                raise ValueError(f"Connection references unknown zone '{conn.zone2}'")

        return self
