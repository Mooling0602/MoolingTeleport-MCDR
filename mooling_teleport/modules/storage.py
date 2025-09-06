import os

from mcdreforged.api.all import ServerInterface
from mooling_teleport.modules.api import TeleportType
from mooling_teleport.utils.uuid import get_uuid

psi = ServerInterface.psi()
config_dir = psi.get_data_folder()


class GetDirectory:
    def __init__(self, module: TeleportType):
        self.module = module

    def public(self) -> str:
        target_path = os.path.join(config_dir, self.module.value)
        os.makedirs(target_path, exist_ok=True)
        return target_path

    def private(self, player: str) -> str:
        uuid = get_uuid(player)
        if uuid is not None:
            target_path = os.path.join(config_dir, self.module.value, uuid)
        else:
            target_path = os.path.join(config_dir, self.module.value, player)
        os.makedirs(target_path, exist_ok=True)
        return target_path
