import mooling_teleport.runtime as rt

from dataclasses import dataclass, field
from datetime import datetime
from mcdreforged.api.all import *
from mooling_teleport.utils import get_time, get_uuid


class TeleportPlayer:
    def __init__(self, selected_player: str):
        self.selected_player = selected_player
        self.target_player = None
        self.server = ServerInterface.psi()

    # 供控制台命令强制传送用
    def execute(self, server: PluginServerInterface, selected: str, target: str):
        server.execute(f"tp {selected} {target}")

    def send_request(self, target_player: str, reverse: bool = False):
        self.target_player = target_player
        src = get_uuid(self.selected_player)
        if not src:
            src = self.selected_player
        target = get_uuid(self.target_player)
        if not target:
            target = self.target_player
        if reverse is True:
            request = TppRequest(src, target, True)
        else:
            request = TppRequest(src, target)
        if request not in rt.tpp_requests:
            rt.tpp_requests.append(request)
            self.server.tell(target_player, "[玩家间传送] 使用!!tpp accept同意你接受到的传送请求！")
        else:
            self.server.tell(self.selected_player, "[玩家间传送] 无法发出重复请求、在当前请求结束前发出新的请求，或目标玩家正在等待处理其他请求，请等待占用状态解除或请求被取消！")
        
    def to_another(self, target_player: str):
        self.execute(self.server, self.selected_player, target_player)

    def to_player_here(self, target_player: str):
        self.execute(self.server, target_player, self.selected_player)

@dataclass
class TppRequest:
    src: str
    target: str
    reverse: bool = field(compare=False, default=False)
    time: datetime = field(compare=False, default_factory=get_time)
    waiting_for_agree: bool = field(compare=False, default=True)

    def __eq__(self, other):
        if not isinstance(other, TppRequest):
            return NotImplemented
        return (self.src == other.src or self.target == other.target) or \
               (self.src == other.target or self.target == other.src)