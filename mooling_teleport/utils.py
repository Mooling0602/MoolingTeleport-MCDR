import locale
import json
import os
import mooling_teleport.runtime as rt

from typing import Callable, Any, Optional
from datetime import datetime, timezone
from mcdreforged.api.all import *

psi = ServerInterface.psi()
server_dir = psi.get_mcdr_config().get('working_directory')


# Usage: @execute_if(lambda: bool | Callable -> bool)
# Ported from: https://github.com/Mooling0602/MoolingUtils-MCDR/blob/main/mutils/__init__.py
def execute_if(condition: bool | Callable[[], bool]):
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            actual_condition = condition() if callable(condition) else condition
            if actual_condition:
                return func(*args, **kwargs)
            return None
        return wrapper
    return decorator

def change_config_and_save(server: PluginServerInterface, option: str, value):
    def get_nested_attr(obj, parts):
        """递归获取嵌套属性"""
        if len(parts) == 1:
            return obj, parts[0]
        next_obj = getattr(obj, parts[0], None)
        if next_obj is None:
            return None, None
        return get_nested_attr(next_obj, parts[1:])

    server.logger.warning(f"正在将插件配置项 {option} 的值修改为 {value}")

    # 分割配置路径
    parts = option.split('.')
    if len(parts) == 0:
        server.logger.error("无效的配置路径！")
        return

    # 递归获取目标对象和属性名
    parent_obj, attr_name = get_nested_attr(rt.config, parts)
    if parent_obj is None or attr_name is None:
        server.logger.error(f"无法修改插件配置项：目标 {option} 不存在！")
        return

    # 获取旧值并验证
    old_value = getattr(parent_obj, attr_name, None)
    if old_value is None:
        server.logger.error(f"无法修改插件配置项：目标 {option} 不存在！")
        return

    # 类型检查（支持自动类型转换）
    try:
        converted_value = type(old_value)(value)
    except (TypeError, ValueError):
        server.logger.error(f"类型不匹配：目标类型为 {type(old_value)}，输入值无法转换")
        return

    # 递归设置属性值
    try:
        setattr(parent_obj, attr_name, converted_value)
    except AttributeError:
        server.logger.error(f"无法修改插件配置项：{attr_name} 是只读属性！")
        return

    # 保存配置
    server.logger.info(f"配置修改成功：{option} §c{old_value}§r -> §a{converted_value}§r")
    server.save_config_simple(config=rt.config, file_name='config.yml')
    server.logger.info("已保存对配置项的修改！")

def enable_force_rcon(server: PluginServerInterface):
    rt.config.force_rcon = True
    server.logger.info("Rcon方案支持已启用！")
    server.save_config_simple(rt.config, 'config.yml')
    server.logger.info("已保存相关配置！")

def get_time(return_str: Optional[bool] = False) -> datetime|str:
    if not return_str:
        return datetime.now(timezone.utc)
    else:
        return datetime.now(timezone.utc).isoformat()
    
def get_pfxed_message(text: str, pfx: str = "[木泠牌传送] ") -> str:
    return pfx + text

def get_time_styled() -> str:
    now = datetime.now()
    if psi.get_mcdr_language() == 'zh_cn':
        locale.setlocale(locale.LC_TIME, 'zh_CN.UTF-8')
    return now.astimezone().strftime("%Y年%m月%d日 %H:%M:%S %A")

def format_time(time: str) -> str:
    try:
        time = datetime.fromisoformat(time)
        if psi.get_mcdr_language() == 'zh_cn':
            locale.setlocale(locale.LC_TIME, 'zh_CN.UTF-8')
        return time.astimezone().strftime("%Y年%m月%d日 %H:%M:%S %A")
    except ValueError:
        raise ValueError("Invalid time format. Expected ISO 8601 format.")

def get_api():
    if rt.config.force_rcon is True:
        import mooling_teleport.rcon as api
        return api
    else:
        try:
            import minecraft_data_api as api # type: ignore
        except ModuleNotFoundError:
            import mooling_teleport.rcon as api
        return api

def get_sorted_data(data: list) -> list:
    sorted_data = sorted(data, key=lambda x: x['time'], reverse=True)
    return sorted_data

def load_json(file_path: str) -> dict|list:
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

def write_to_json(data: dict|list, file_path: str):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def get_uuid(player: str) -> str|None:
    usercache = load_json(os.path.join(server_dir, 'usercache.json'))
    for i in usercache:
        if i.get('name', None) == player:
            uuid = i.get('uuid', None)
            return uuid
    return None
