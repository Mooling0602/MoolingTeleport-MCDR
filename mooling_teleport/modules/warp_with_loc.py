## 对接Location Marker
import os
from typing import Union

from mooling_teleport.utils import load_json
from mooling_teleport.modules.data_templates import Location, Position


def get_dim_key(dim: Union[int, str]) -> str:
	dimension_convert = {0: 'minecraft:overworld', -1: 'minecraft:the_nether', 1: 'minecraft:the_end'}
	return dimension_convert.get(dim, dim)

class LocationMarkerTeleport:
    def __init__(self):
        self.data_path = os.path.join("config", "location_marker", "locations.json")
        if not os.path.exists(self.data_path):
            raise RuntimeError('location_marker data is not found!')

    def get_locname_list(self) -> list:
        locations = load_json(self.data_path)
        if isinstance(locations, list):
            locnames = []
            for i in locations:
                locnames.append(i.get("name", None))
            return locnames
        else:
            raise ValueError('target data is not a list!')
        
    def get_location(self, locname: str) -> "Location":
        locations = load_json(self.data_path)
        if isinstance(locations, list):
            for i in locations:
                name = i.get("name", None)
                if name != locname:
                    continue
                position = {
                    "pos": i.get("pos", None),
                    "dim": get_dim_key(i.get("dim", None))
                }
                result = Location(position=Position.from_dict(position), name=name)
                return result
            return None
        else:
            raise ValueError('target data is not a list!')