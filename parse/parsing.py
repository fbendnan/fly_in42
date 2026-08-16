from typing import Any, Optional, Dict, List
from parse.hub_model import Zone
from parse.connection import Connection


class ParseConfig:
    def __init__(self, file_name: str) -> None:
        self.file_name: str = file_name
        self.nb_drones: int = 0
        self.start_hub: Optional[Dict[str, Any]] = None
        self.end_hub: Optional[Dict[str, Any]] = None
        self.hubs: List[Dict[str, Any]] = []
        self.hubs_name: List[str] = []
        self.connections: List[Dict[str, Any]] = []

    def is_connected_hub(self, hub: str) -> bool:
        for c in self.connections:
            if c["zone1"] == hub or c["zone2"] == hub:
                return True

        return False

    def parser(self) -> "ParseConfig":
        with open(self.file_name) as f:
            lines = f.readlines()

        line_no = 0
        for raw_line in lines:
            stripped_line = raw_line.strip()
            if not stripped_line or stripped_line.startswith("#"):
                continue
            if '#' in stripped_line:
                n_stripped_line = stripped_line.split('#', 1)
                stripped_line = n_stripped_line[0]
            line_no += 1
            parts = stripped_line.split(":", 1)
            if len(parts) != 2:
                raise ValueError(f"Line {line_no}: Missing colon separator")
            key = parts[0].strip()
            value = parts[1].strip()
            if line_no == 1:
                if key != "nb_drones":
                    raise ValueError(
                        f"Line {line_no}: First line must be 'nb_drones'"
                    )
                try:
                    self.nb_drones = int(value)
                except ValueError:
                    raise ValueError(
                        f"Line {line_no}: nb_drones must be integer, "
                        f"got '{value}'"
                    )
                if self.nb_drones < 1:
                    raise ValueError(
                        f"Line {line_no}: nb_drones must be ≥ 1, "
                        f"got {self.nb_drones}"
                    )
                continue

            try:
                if key == "start_hub":
                    validated_data = Zone.validate_hub(value)
                    if self.start_hub is not None:
                        raise ValueError("Duplicted start zone")
                    self.hubs_name.append(validated_data["name"])
                    self.start_hub = validated_data

                elif key == "end_hub":
                    validated_data = Zone.validate_hub(value)
                    if self.end_hub is not None:
                        raise ValueError("Duplicted end zone")
                    self.hubs_name.append(validated_data["name"])
                    self.end_hub = validated_data

                elif key == "hub":
                    validated_data = Zone.validate_hub(value)

                    if validated_data["name"] in self.hubs_name:
                        raise ValueError(
                            f"Duplicate zone name: {validated_data['name']}"
                        )

                    for h in self.hubs:
                        if (
                            h["x"] == validated_data["x"]
                            and h["y"] == validated_data["y"]
                        ):
                            raise ValueError(
                                f"Duplicate coordinates "
                                f"({validated_data['x']}, "
                                f"{validated_data['y']})"
                            )

                    if (
                        self.start_hub is not None
                        and validated_data["x"] == self.start_hub["x"]
                        and validated_data["y"] == self.start_hub["y"]
                    ):
                        raise ValueError(
                            f"Hub coordinates ({validated_data['x']}, "
                            f"{validated_data['y']}) conflict with start hub"
                        )

                    # start and end has same cordinate testing
                    if (
                        self.end_hub is not None
                        and validated_data["x"] == self.end_hub["x"]
                        and validated_data["y"] == self.end_hub["y"]
                    ):
                        raise ValueError(
                            f"Hub coordinates ({validated_data['x']}, "
                            f"{validated_data['y']}) conflict with end hub"
                        )

                    self.hubs_name.append(validated_data["name"])
                    self.hubs.append(validated_data)

                elif key == "connection":
                    validated_data = Connection.validate_connection(value)
                    zone1 = validated_data["zone1"]
                    zone2 = validated_data["zone2"]

                    if (
                        zone1 not in self.hubs_name
                        or zone2 not in self.hubs_name
                    ):
                        raise ValueError(
                            f"Connection {zone1}-{zone2} has unknown zone"
                        )

                    for c in self.connections:
                        if (
                            c["zone1"] == zone1
                            and c["zone2"] == zone2
                        ) or (
                            c["zone1"] == zone2
                            and c["zone2"] == zone1
                        ):
                            raise ValueError(
                                f"Duplicate connection: {zone1}-{zone2}"
                            )

                    self.connections.append(validated_data)

                else:
                    raise ValueError(f"Unknown keyword '{key}'")

            except Exception as e:
                raise ValueError(f"Line {line_no}: {e}")

        if self.start_hub is None:
            raise ValueError("Missing 'start_hub' definition")

        if self.end_hub is None:
            raise ValueError("Missing 'end_hub' definition")

        if self.start_hub["name"] == self.end_hub["name"]:
            raise ValueError(
                "start and end zone should be different"
            )
        if (self.start_hub["x"] == self.end_hub["x"]
                and self.end_hub["y"] == self.start_hub["y"]):
            raise ValueError(
                "start and end cordinate should be different"
            )
        for h in self.hubs:
            if ((h["x"] == self.start_hub["x"]
                    and self.start_hub["y"] == h["y"])
                    or (self.end_hub["x"] == h["x"]
                        and self.end_hub["y"] == h["y"])):
                raise ValueError(
                    "Cordinate duplication"
                )
        # for hub in self.hubs_name:
        #     if not self.is_connected_hub(hub):
        #         raise ValueError(f"{hub} is not connected")

        all_zone_names = {
            self.start_hub["name"],
            self.end_hub["name"],
        }
        all_zone_names.update(hub["name"] for hub in self.hubs)

        for conn in self.connections:
            if conn["zone1"] not in all_zone_names:
                raise ValueError(
                    f"Connection references unknown zone "
                    f"'{conn['zone1']}'"
                )

            if conn["zone2"] not in all_zone_names:
                raise ValueError(
                    f"Connection references unknown zone "
                    f"'{conn['zone2']}'"
                )

        return self
