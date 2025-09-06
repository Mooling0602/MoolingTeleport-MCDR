import os
import re
from typing import Optional

from mooling_teleport.utils import load_json, server_dir


def get_uuid(player: str) -> Optional[str]:
    # noinspection SpellCheckingInspection
    def from_usercache() -> Optional[str]:
        usercache = load_json(os.path.join(server_dir, "usercache.json"))
        for i in usercache:
            if i.get("name", None) == player:
                uuid = i.get("uuid", None)
                return uuid
        return None

    def from_whitelist() -> Optional[str]:
        whitelist = load_json(os.path.join(server_dir, "whitelist.json"))
        for i in whitelist:
            if i.get("name", None) == player:
                uuid = i.get("uuid", None)
                return uuid
        return None

    result = from_whitelist()
    if result is None:
        result = from_usercache()
    return result


def check_uuid_valid(uuid: str) -> bool:
    uuid_regex = re.compile(
        r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    )
    return bool(uuid_regex.match(uuid))


def get_player(uuid: str) -> Optional[str]:
    # noinspection SpellCheckingInspection
    def from_usercache() -> Optional[str]:
        usercache = load_json(os.path.join(server_dir, "usercache.json"))
        for i in usercache:
            if i.get("uuid", None) == uuid:
                player = i.get("name", None)
                return player
        return None

    def from_whitelist() -> Optional[str]:
        whitelist = load_json(os.path.join(server_dir, "whitelist.json"))
        for i in whitelist:
            if i.get("uuid", None) == uuid:
                player = i.get("name", None)
                return player
        return None

    result = from_whitelist()
    if result is None:
        result = from_usercache()
    return result
