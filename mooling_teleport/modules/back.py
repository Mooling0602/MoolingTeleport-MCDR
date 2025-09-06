import os
from typing import Optional

import mooling_teleport.runtime as rt
from mooling_teleport.modules.api import TeleportType
from mooling_teleport.modules.data_templates import Position
from mooling_teleport.modules.storage import GetDirectory
from mooling_teleport.utils import get_sorted_data, load_json
from mooling_teleport.utils.uuid import get_uuid


class BackTeleport:
    def __init__(self, player: str):
        self.player = player
        self.storage_dir = GetDirectory(TeleportType.Back).private(self.player)
        died_history_path = os.path.join(self.storage_dir, "died_history.json")
        if os.path.exists(died_history_path):
            self.died_history_path = died_history_path
        else:
            self.died_history_path = None

    def get_died_latest(self) -> Optional[Position]:
        raw_data = load_json(self.died_history_path) if self.died_history_path else []
        data = get_sorted_data(raw_data)
        if len(data) > 0:
            record = data[0]
            position = Position.from_dict(record)
            return position
        return None

    def get_died_list(self) -> list[Position]:
        data = load_json(self.died_history_path) if self.died_history_path else []
        result = get_sorted_data(data)
        for i in result:
            position = Position.from_dict(i)
            idx = result.index(i)
            result[idx] = position
        return result

    def get_cached_position(self) -> Optional[Position]:
        uuid = get_uuid(self.player)
        if uuid is not None:
            position = rt.cached_positions.get(uuid, None)
        else:
            position = rt.cached_positions.get(self.player, None)
        return position
