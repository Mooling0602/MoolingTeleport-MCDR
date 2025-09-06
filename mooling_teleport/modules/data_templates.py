from typing import Optional

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
            raise ValueError("length of the pos is not 3!")
        for i in self.pos:
            if not isinstance(i, float):
                try:
                    idx = self.pos.index(i)
                    self.pos[idx] = float(i)
                except Exception as e:
                    psi.logger.error(f"error reading position data: {e}")
        if not isinstance(self.dim, str):
            raise ValueError("dim is invalid!")
        if not self.dim.startswith("minecraft"):
            if rt.config.non_vanilla_dim_warning:
                psi.logger.warning(
                    "传入了一个非原版维度的坐标数据，请确认该维度实际存在！"
                )
                psi.logger.info(
                    "使用!!mtp allow_non_vanilla_dim或修改插件配置以关闭此警告。"
                )
        if self.dim == "":
            raise TypeError("empty dim is not allowed!")

    @classmethod
    def from_dict(cls, data: dict) -> "Position":
        pos: Optional[list | dict] = data.get("pos", data.get("position", None))
        dim: Optional[str] = data.get("dim", data.get("dimension", None))
        if not isinstance(pos, list | dict) or not isinstance(dim, str):
            raise ValueError("Dict data is invalid!")
        # 修复：确保只在 pos 是字典且不为 None 时才执行字典操作
        if (
            isinstance(pos, dict)
            and pos is not None
            and all(k in pos for k in ("x", "y", "z"))
        ):
            values = [pos.get(k) for k in ("x", "y", "z")]
            if all(v is not None for v in values):
                pos = [float(v) for v in values]
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
        position_data: Optional[dict] = data.get("position", None)
        name: Optional[str] = data.get("name", None)
        if position_data is None or name is None:
            raise ValueError("Dict data is invalid!")
        position = Position.from_dict(position_data)
        keys_to_exclude = {"position", "name"}
        other = {k: v for k, v in data.items() if k not in keys_to_exclude}
        return cls(position=position, name=name, other=other)
