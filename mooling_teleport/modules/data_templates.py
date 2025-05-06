import mooling_teleport.runtime as rt

from dataclasses import dataclass
from mooling_teleport.utils import psi

@dataclass
class Position:
    pos: list[float]
    dim: str
    other: dict = None

    def __post_init__(self):
        if len(self.pos) != 3:
            raise ValueError('length of the pos is not 3!')
        for i in self.pos:
            if not isinstance(i, float):
                self.pos[self.pos.index(i)] = float(i)
        if not isinstance(self.dim, str):
            raise ValueError('dim is invalid!')
        if not self.dim.startswith("minecraft"):
            if rt.config.non_vanilla_dim_warning:
                psi.logger.warning("传入了一个非原版维度的坐标数据，请确认该维度实际存在！")
                psi.logger.info("使用!!mtp allow_non_vanilla_dim或修改插件配置以关闭此警告。")
        if self.dim == "":
            raise TypeError('empty dim is not allowed!')

    @classmethod
    def from_dict(cls, data: dict) -> "Position":
        pos = data.get('pos', data.get('position', None))
        dim = data.get('dim', data.get('dimension', None))
        if pos is None or dim is None:
            raise ValueError('Dict data is invalid!')
        if isinstance(pos, dict) and all(k in pos for k in ("x", "y", "z")):
            pos = [float(pos[k]) for k in ("x", "y", "z")]
        keys_to_exclude = {"pos", "dim", "position", "dimension"}
        other = {k: v for k, v in data.items() if k not in keys_to_exclude}
        return cls(pos=pos, dim=dim, other=other)

@dataclass
class Location:
    position: Position
    name: str
    other: dict = None

    @classmethod
    def from_dict(cls, data: dict) -> "Location":
        position = Position.from_dict(data.get('position', None))
        name = data.get('name', None)
        keys_to_exclude = {"position", "name"}
        other = {k: v for k, v in data.items() if k not in keys_to_exclude}
        return cls(position=position, name=name, other=other)