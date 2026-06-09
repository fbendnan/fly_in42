from pydantic import BaseModel, model_validator, Field
from typing import Optional, Literal
import re


class Zone(BaseModel):
    name: str = Field(..., min_length=1)
    x: int = Field(...)
    y: int = Field(...)
    zone: Literal["normal", "priority", "restricted", "blocked"] = Field(
        default="normal"
    )
    max_drones: int = Field(default=1)
    color: Optional[str] = None
    neighbors: list = Field(default_factory=list)
    cost: int = 0

    @classmethod
    def validate_hub(cls, value):
        pattern = (
            r"^(?P<name>\w+)\s+(?P<x>-?\d+)\s+(?P<y>-?\d+)(?:\s*\[(?P<options>.*?)\])?$"
        )
        match = re.match(pattern, value)
        if not match:
            raise ValueError(f"Invalid hub format: {value}")

        name = match.group("name")
        x = int(match.group("x"))
        y = int(match.group("y"))
        options_str = match.group("options")

        options_dict = {}
        if options_str:
            pairs = re.findall(r"(\w+)=([^\s\]]+)", options_str)
            for key, val in pairs:
                if key in options_dict:
                    raise ValueError(f"Duplicate metadata key: {key}")
                options_dict[key] = val

        allowed_keys = {"zone", "max_drones", "color"}
        for key in options_dict:
            if key not in allowed_keys:
                raise ValueError(
                    f"Unknown metadata key '{key}' in hub line. Allowed: {allowed_keys}"
                )

        zone_type = options_dict.get("zone", "normal")
        if zone_type not in ["normal", "priority", "restricted", "blocked"]:
            raise ValueError(f"Invalid zone type: {zone_type}")

        max_drones_val = options_dict.get("max_drones", 1)
        try:
            max_drones_int = int(max_drones_val)
        except ValueError:
            raise ValueError(f"max_drones must be an integer, got '{max_drones_val}'")
        if max_drones_int < 1:
            raise ValueError(f"max_drones must be positive, got {max_drones_int}")

        color_val = options_dict.get("color")  # None if absent

        return {
            "name": name,
            "x": x,
            "y": y,
            "zone": zone_type,
            "max_drones": max_drones_int,
            "color": color_val,
        }
