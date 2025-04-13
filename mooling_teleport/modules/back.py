import os

from mooling_teleport.utils import get_sorted_data, load_json
from mooling_teleport.modules.storage import GetDirectory
from mooling_teleport.modules.data_templates import Position
from mooling_teleport.modules.api import position_list_to_str, TeleportType, TeleportPosition


class BackTeleport:
    def __init__(self, player: str):
        self.player = player
        self.storage_dir = GetDirectory(TeleportType.Back).private(self.player)
        died_history_path = os.path.join(self.storage_dir, 'died_history.json')
        if os.path.exists(died_history_path):
            self.died_history_path = died_history_path
        else:
            self.died_history_path = None
        self.tp = TeleportPosition()

    def go_to_died_latest(self):
        raw_data = load_json(self.died_history_path) if self.died_history_path else []
        data = get_sorted_data(raw_data)
        if len(data) > 0:
            record = data[0]
            self.tp.by_dict_data(record, self.player)

    def get_died_list(self) -> list[Position]:
        data = load_json(self.died_history_path) if self.died_history_path else []
        result = get_sorted_data(data)
        for i in result:
            position = Position.from_dict(i)
            idx = result.index(i)
            result[idx] = position
        return result

    def get_pos_before_cmd(self) -> dict:
        pass