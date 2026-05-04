from pydantic import BaseModel, model_validator, Field
from typing import Optional, Literal
import re

class HubModel(BaseModel):
    name : str = Field(..., min_length = 1)
    x : int = Field(...)
    y : int = Field(...)
    zone: Literal["normal", "priority", "restricted", "blocked"] = Field(default='normal')
    max_drones : int = Field(default=1)
    color : Optional[str] = None

    @classmethod
    @model_validator(mode="before")
    def validate_hub(cls, string: str):
        pattern = r"^(?P<name>\w+)\s+(?P<x>\d+)\s+(?P<y>\d+)(?:\s*\[(?P<options>.*?)\])?$"

        matchs = re.match(pattern, string)
        if not matchs:
            raise ValueError(f"Invalid hub format: {string}")
        if matchs:
            name = matchs.group('name')
            x = int(matchs.group('x'))
            y = int(matchs.group('y'))
            options = matchs.group('options')
        options_dict = {}
        if options:
            pairs = re.findall(r'(\w+)=([^\s\]]+)', options)
            for key, value in pairs:
                if key in options_dict:
                    raise ValueError(f"Duplicate key {key}")
                options_dict[key] = value
        zone_type = options_dict.get('zone', 'normal')
        if zone_type not in ["normal", "priority", "restricted", "blocked"]:
            raise ValueError(f"Invalid zone type: {zone_type}")
        
        max_drones = options_dict.get('max_drones', 1)
        if int(max_drones) < 1:
            raise ValueError(f"Invalid max_drones: {max_drones}")

        color_val = options_dict.get('color')
        data = {
            "name": name,
            "x": x,
            "y": y,
            "zone": zone_type,
            "max_drones": int(max_drones),
            "color": color_val,
        }

        return data