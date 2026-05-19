from pydantic import BaseModel, model_validator, Field
import re

class Connection(BaseModel):
    zone1: str = Field(..., min_length=1)
    zone2: str = Field(..., min_length=1)
    max_link_capacity: int = Field(default=1)

    @classmethod
    def validate_connection(cls, value):
        pattern = r"^(?P<zone1>\w+)\s*-\s*(?P<zone2>\w+)(?:\s*\[(?P<options>.*?)\])?$"
        match = re.match(pattern, value)
        if not match:
            raise ValueError(f"Invalid connection format: {value}")

        zone1 = match.group('zone1')
        zone2 = match.group('zone2')
        options_str = match.group('options')

        options_dict = {}
        if options_str:
            pairs = re.findall(r'(\w+)=([^\s\]]+)', options_str)
            for key, val in pairs:
                if key in options_dict:
                    raise ValueError(f"Duplicate metadata key: {key}")
                options_dict[key] = val

        for key in options_dict:
            if key != "max_link_capacity":
                raise ValueError(f"Unknown metadata key '{key}' in connection. Only 'max_link_capacity' allowed.")

        max_cap = options_dict.get('max_link_capacity', 1)
        try:
            max_cap_int = int(max_cap)
        except ValueError:
            raise ValueError(f"max_link_capacity must be an integer, got '{max_cap}'")
        if max_cap_int < 1:
            raise ValueError(f"max_link_capacity must be positive, got {max_cap_int}")
        return {
            "zone1": zone1,
            "zone2": zone2,
            "max_link_capacity": max_cap_int,
        }
