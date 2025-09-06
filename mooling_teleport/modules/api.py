import mooling_teleport.runtime as rt

from dataclasses import dataclass
from enum import Enum
from typing import Optional
from mcdreforged.api.all import ServerInterface, new_thread
from mooling_teleport.utils import get_api, get_time, get_uuid, get_player
from mooling_teleport.modules.data_templates import Position

psi = ServerInterface.psi()


def get_position(player: str) -> dict:
    api = get_api()
    position: list = api.get_player_info(player, "Pos")
    dimension: str = api.get_player_info(player, "Dimension")
    if (
        not isinstance(position, list)
        or len(position) != 3
        or not isinstance(dimension, str)
    ):
        psi.tell(
            player,
            "[木泠牌传送] 无法获取你的位置数据！请联系管理员处理后台的插件报错。",
        )
        raise RuntimeError(
            "Invalid data received, please use rcon or disable oher similar plugins."
        )
    result = {"position": position, "dimension": dimension}
    return result


def position_list_to_str(position: list) -> str:
    x = position[0]
    y = position[1]
    z = position[2]
    return f"{x} {y} {z}"


@new_thread("CachePos(mooling_teleport)")
def cache_position(player: str):
    position = Position.from_dict(get_position(player))
    time_data = {"time": get_time(return_str=True)}
    position.other = time_data
    uuid = get_uuid(player)
    if uuid is not None:
        rt.cached_positions[uuid] = position
    else:
        rt.cached_positions[player] = position


class TeleportType(Enum):
    Back = "back"
    Home = "home"
    TeleportPlayer = "tpp"
    TeleportPosition = "tp"
    Warp = "warp"


class TeleportPosition:
    def __init__(self, xyz_pos: Optional[str] = None, dimension: Optional[str] = None):
        self.xyz_pos = xyz_pos
        self.dimension = dimension
        self.server = ServerInterface.psi()

    def by_dict_data(self, data: dict, target: str):
        position = Position.from_dict(data)
        xyz_pos = position_list_to_str(position.pos)
        if xyz_pos is not None:
            self.server.execute(f"execute in {position.dim} run tp {target} {xyz_pos}")

    def by_class_position(self, data: Position, target: str):
        xyz_pos = position_list_to_str(data.pos)
        self.server.execute(f"execute in {data.dim} run tp {target} {xyz_pos}")

    def __call__(self, target: str):
        self.server.execute(
            f"execute in {self.dimension} run tp {target} {self.xyz_pos}"
        )


@dataclass
class Player:
    name: str = None
    uuid: str = None

    @classmethod
    def by_uuid(cls, uuid: str) -> "Player":
        name = get_player(uuid)
        return cls(name=name, uuid=uuid)

    @classmethod
    def by_name(cls, name: str) -> "Player":
        uuid = get_uuid(name)
        return cls(name=name, uuid=uuid)
