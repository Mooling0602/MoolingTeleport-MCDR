import os
import mooling_teleport.runtime as rt

from mcdreforged.api.all import *
from mooling_teleport.config import config_loader
from mooling_teleport.commands import command_register
from mooling_teleport.modules.storage import GetDirectory
from mooling_teleport.modules.api import TeleportType, get_position
from mooling_teleport.utils import enable_force_rcon, get_sorted_data, get_time, get_pfxed_message, load_json, write_to_json

builder = SimpleCommandBuilder()


confirm_config_plz = None
confirm_request_time = None

def on_load(server: PluginServerInterface, prev_module):
    global confirm_config_plz
    server.logger.info("正在启动插件的配置加载器……")
    init_status, config = config_loader(server)
    rt.init_status = init_status
    rt.config = config
    server.logger.info("正在注册死亡事件监听器……")
    server.register_event_listener("PlayerDeathEvent", on_player_death)
    server.logger.info("正在注册插件命令......")
    command_register(server)
    server.logger.info("插件已完成载入，正在检查杂项……")
    if rt.init_status is True and rt.config.force_rcon is False:
        confirm_config_plz = True
        if server.is_server_startup() is False:
            server.logger.warning("有待手动确认的事项，将在服务器启动完成后再发出提醒，避免被日志刷屏干扰。")
    if server.is_server_startup():
        server.say(get_pfxed_message("插件载入完成！"))
        on_server_startup(server)

def on_unload(server: PluginServerInterface):
    server.say(get_pfxed_message("插件正在卸载，相关功能将无法再使用！"))

def on_server_startup(server: PluginServerInterface):
    if confirm_config_plz is True:
        init_plugin_rcon(server)
        rt.init_status = False
    import mooling_teleport.rcon as rcon_module
    if rcon_module.server is None and server.is_rcon_running():
        rcon_module.set_server(server_instance=server)
        server.logger.info("插件的Rcon支持模块已初始化完成！")

def init_plugin_rcon(server: PluginServerInterface):
    global confirm_request_time
    server.logger.info("这是您首次启动木泠的传送插件，感谢使用！")
    server.logger.info("插件默认使用Minecraft Data API以获取玩家的位置数据，但当多个插件同时对同一玩家调用该API时，会出现数据错乱问题。")
    server.logger.info("这个问题无法解决，故只能改用Rcon方案才能避免这种情况。")
    if server.is_rcon_running() is False:
        server.logger.warning("当前MCDR的Rcon功能不可用，需要使用带有Rcon功能的服务端并正确配置！")
        server.logger.warning("建议使用!!MCDR plg install init_server安装初始化插件，以自动化完成配置，你可能需要安装后重启MCDR和服务器才能生效！")
        server.logger.info("配置好Rcon后，使用!!mtp use_rcon来启用插件内置的Rcon方案支持。")
    else:
        server.logger.info("MCDR的Rcon功能正常！")
        server.logger.info("您可以使用!!mtp use_rcon来启用插件内置的Rcon方案支持。")
        server.logger.info("如果您懒得输入完整命令，可以在30秒内在控制台发送y直接进行确认，这个命令是一次性的。")
        confirm_request_time = get_time()

def on_info(server: PluginServerInterface, info: Info):
    if info.is_from_console and info.content == "y":
        time_now = get_time()
        if confirm_request_time is None or (time_now - confirm_request_time).total_seconds() <= 30:
            info.cancel_send_to_server()
            enable_force_rcon(server)

@new_thread('GetPlayerDeathPos(mooling_teleport)')
def on_player_death(server: PluginServerInterface, player: str, event: str, content: list):
    server.logger.info(f"[木泠牌传送] {player} 死掉了，正在记录其位置......")
    storage_dir = GetDirectory(TeleportType.Back).private(player)
    storage_path = os.path.join(storage_dir, 'died_history.json')
    if not os.path.exists(storage_path):
        write_to_json([], storage_path)
    data: list = get_sorted_data(load_json(storage_path))
    position = get_position(player)
    position["time"] = get_time(return_str=True)
    for i in content:
        if i.locale == "zh_cn":
            died_message = i.raw
    position["reason"] = died_message
    position["type"] = event
    data.insert(0, position)
    max_record = rt.config.back.max_record
    if len(data) > max_record:
        for i in range(len(data)):
            if i > max_record - 1:
                data.remove(data[i])
    write_to_json(data, storage_path)
    server.logger.info(f"{player} 的死亡位置已记录到 {storage_path}。")
    server.tell(player, get_pfxed_message("已记录您的本次死亡位置，可使用!!back快速返回"))
