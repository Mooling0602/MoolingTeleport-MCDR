import os
import mooling_teleport.runtime as rt

from mcdreforged.api.all import *
from datetime import datetime
from mooling_teleport.utils import StrConverter, enable_force_rcon, get_uuid
from mooling_teleport.help_page import help_info, help_menu, get_back_page
from mooling_teleport.modules.api import TeleportPosition, TeleportType
from mooling_teleport.modules.back import BackTeleport, cache_position
from mooling_teleport.modules.storage import GetDirectory
from mooling_teleport.utils import format_time, change_config_and_save, get_pfxed_message

psi = ServerInterface.psi()
builder = SimpleCommandBuilder()


def command_register(server: PluginServerInterface):
    builder.arg('num', Integer)
    builder.arg('option', Text).suggests(lambda: list(vars(rt.config).keys()))
    builder.arg('value', Text)
    builder.register(server)

@builder.command('!!mtp')
def on_command_plg_main(src: CommandSource, ctx: CommandContext):
    src.reply(help_info)

@builder.command('!!mtp help')
def on_command_help_menu(src: CommandSource, ctx: CommandContext):
    src.reply(help_menu)

@builder.command('!!mtp help back')
def on_command_help_back_page(src: CommandSource, ctx: CommandContext):
    src.reply(get_back_page(src))

@builder.command('!!mtp debug config show_options')
def on_list_plugin_configs(src: CommandSource, ctx: CommandContext):
    src.reply(list(vars(rt.config).keys()))

@builder.command('!!mtp debug config print')
def on_print_plugin_config(src: CommandSource, ctx: CommandContext):
    src.reply(rt.config)

@builder.command('!!mtp debug config print <option>')
def on_print_plugin_config_option(src: CommandSource, ctx: CommandContext):
    src.reply(getattr(rt.config, ctx['option'], None))

@builder.command('!!mtp debug command print_tree')
def on_print_plugin_command_tree(src: CommandSource, ctx: CommandContext):
    builder.print_tree(src.reply)

@builder.command('!!mtp debug back tp')
def on_debug_back_tp(src: CommandSource, ctx: CommandContext):
    src.reply(rt.cached_positions)

@builder.command('!!mtp set config <option> <value>')
def on_set_plugin_config_any(src: CommandSource, ctx: CommandContext):
    if not src.has_permission(4):
        src.reply("权限不足，需最高权限！")
        return
    if src.is_player:
        src.reply("请在控制台上查看配置修改结果！")
    server = src.get_server().psi()
    value = StrConverter()(ctx['value'])
    change_config_and_save(server, ctx['option'], value)

@builder.command('!!mtp powerwash')
@builder.command('!!mtp reset config all')
def on_plugin_powerwash(src: CommandSource, ctx: CommandContext):
    server = src.get_server().psi()
    def do_powerwash():
        src.reply("你已确认操作，正在删除插件主配置实际文件……")
        src.reply("该操作不可逆！")
        config_dir = server.get_data_folder()
        config_file = os.path.join(config_dir, 'config.yml')
        os.remove(config_file)
        src.reply("删除完成，开始重载插件！")
        server.reload_plugin(server.get_self_metadata().id)
    if not src.has_permission(4):
        src.reply("权限不足，需最高权限！")
        return
    if rt.do_powerwash is False:
        src.reply("将删除插件主配置，若确定，请再执行一遍指令！")
        src.reply("各种坐标数据将会被保留，如有需要请手动删除！")
        rt.do_powerwash = True
    else:
        do_powerwash()

@builder.command('!!mtp powerwash --confirm')
@builder.command('!!mtp reset config all --confirm')
def do_plugin_powerwash(src: CommandSource, ctx: CommandContext):
    if not src.has_permission(4):
        src.reply("权限不足，需最高权限！")
        return
    rt.do_powerwash = True
    on_plugin_powerwash(src, ctx)

@builder.command('!!mtp powerwash --cancel')
@builder.command('!!mtp reset config all --cancel')
def cancel_plugin_powerwash(src: CommandSource, ctx: CommandContext):
    if not src.has_permission(4):
        src.reply("权限不足，需最高权限！")
        return
    rt.do_powerwash = False
    src.reply("已取消插件重置条件，若确需重置插件，请重新进行确认流程。")

@builder.command('!!mtp use_rcon')
def on_command_mtp_use_rcon(src: CommandSource, ctx: CommandContext):
    if not src.has_permission_higher_than(3):
        src.reply("权限不足！")
        return
    enable_force_rcon(src.get_server().psi())
    if src.is_player:
        src.reply("操作执行完成！")

# 回溯传送主命令
@builder.command('!!back')
@builder.command('!!mooling_teleport:back')
def on_command_back(src: CommandSource, ctx: CommandContext):
    if not src.is_player:
        src.reply("请以玩家身份运行命令！")
        return
    back = BackTeleport(src.player)
    died_position = back.get_died_latest()
    cache_position = back.get_cached_position()
    if not died_position and not cache_position:
        src.reply("没有检查到你的历史传送数据！")
        return
    src.reply("默认回溯到离当前时间最近的先前位置。")
    src.reply("若要返回死亡点，请使用!!back died；")
    src.reply("若要回溯到任意传送指令生效前的位置，请使用!!back tp或!!reback")
    if died_position and cache_position:
        died_time = died_position.other['time']
        tp_time = cache_position.other['time']
        died_time = datetime.fromisoformat(died_time)
        tp_time = datetime.fromisoformat(tp_time)
        if tp_time > died_time:
            on_command_back_tp(src, ctx)
        else:
            on_command_back_died(src, ctx)
    else:
        if not cache_position:
            on_command_back_died(src, ctx)
        if not died_position:
            on_command_back_tp(src, ctx)

@builder.command('!!back tp')
@builder.command('!!mooling_teleport:back tp')
@builder.command('!!back teleport')
@builder.command('!!mooling_teleport:back teleport')
@builder.command('!!reback')
@builder.command('!!mooling_teleport:reback')
def on_command_back_tp(src: CommandSource, ctx: CommandContext):
    if not src.is_player:
        src.reply("请以玩家身份运行命令！")
        return
    back = BackTeleport(src.player)
    position = back.get_cached_position()
    tp = TeleportPosition()
    if position:
        tp.by_class_position(position, src.player)
        src.reply("已将你回溯至上次执行传送相关命令前所在位置！")
        uuid = get_uuid(src.player)
        if uuid:
            del rt.cached_positions[uuid]
        else:
            del rt.cached_positions[src.player]
    else:
        src.reply("无法回溯你的位置：无数据！")
        
@builder.command('!!back died')
@builder.command('!!mooling_teleport:back died')
def on_command_back_died(src: CommandSource, ctx: CommandContext):
    if not src.is_player:
        src.reply("请以玩家身份运行命令！")
        return
    back = BackTeleport(src.player)
    position = back.get_died_latest()
    if position:
        cache_position(src.player)
    else:
        src.reply("你没有历史死亡记录（尚未死过或数据已被删除），故不会执行任何操作！")
        return
    tp = TeleportPosition()
    tp.by_class_position(position, src.player)
    src.reply("已传送到离当前时间最近的一个死亡地点！（如果没有历史数据则无法传送）")

@builder.command('!!back died <num>')
@builder.command('!!mooling_teleport:back died <num>')
def on_command_back_died_num(src: CommandSource, ctx: CommandContext):
    if not src.is_player:
        src.reply("请以玩家身份运行命令！")
        return
    num = ctx['num']
    died_history: list = BackTeleport(src.player).get_died_list()
    if num > len(died_history) or num < 1:
        src.reply("参数不合法，或该次死亡记录不存在！")
        return
    count = len(died_history) + 1
    for i in died_history:
        count -= 1
        if count == num:
            TeleportPosition().by_class_position(i, src.player)
            src.reply(f"已传送到第 {num} 次死亡的地点！")

@builder.command('!!back died list')
@builder.command('!!mooling_teleport:back died list')
def on_command_back_died_list(src: CommandSource, ctx: CommandContext):
    if not src.is_player:
        src.reply("请以玩家身份运行命令！")
        return
    src.reply(get_pfxed_message("下面是你的死亡地点历史"))
    died_history: list = BackTeleport(src.player).get_died_list()
    count = len(died_history) + 1
    for i in died_history:
        count -= 1
        start_message = f"第 {count} 个死亡记录："
        if count == len(died_history):
            src.reply(f"第 {count} 个死亡记录（最新）：")
        else:
            src.reply(start_message)
        if i.other.get('time', None) is not None:
            src.reply(f"- 死亡时间：{format_time(i.other['time'])}")
        else:
            src.reply("§c警告：该记录缺少时间信息！")
        src.reply(f"- 死亡坐标：{i.pos}")
        src.reply(f"- 死亡维度：{i.dim}")
        if i.other.get('reason', None) is not None:
            src.reply(f"- 死亡原因：{i.other['reason']}")
        if i.other.get('type', None) is not None:
            src.reply(f"- 死亡类型：{i.other['type']}")

@builder.command('!!back clear')
def on_command_back_clear(src: CommandSource, ctx: CommandContext):
    if src.is_console:
        src.reply("需指定要操作的玩家，用法：§c!!back clear <player> [--confirm]§r")
        return
    uuid = get_uuid(src.player)
    do_clear = False
    if uuid:
        if not uuid in rt.clear_back_data:
            rt.clear_back_data.append(uuid)
        else:
            do_clear = True
    else:
        if not src.player in rt.clear_back_data:
            rt.clear_back_data.append(src.player)
        else:
            do_clear = True
    if do_clear:
        for i in rt.clear_back_data:
            if i == uuid or i == src.player:
                on_command_back_clear_confirm(src, ctx)
                return
    src.reply("此操作将清除你执行上次传送命令前所在位置和全部死亡记录！")
    src.reply("如果确认要清除你的数据，请§c再次运行这条命令！§r否则，要反悔的话，可以使用§a!!back clear --cancel§r")

@builder.command('!!back clear --cancel')
def on_command_back_clear_cancel(src: CommandSource, ctx: CommandContext):
    if src.is_console:
        src.reply("需指定要操作的玩家，用法：§a!!back clear <player> --cancel")
        return
    uuid = get_uuid(src.player)
    if uuid:
        if uuid in rt.clear_back_data:
            rt.clear_back_data.remove(uuid)
    else:
        if src.player in rt.clear_back_data:
            rt.clear_back_data.remove(src.player)
    if '--cancel' in ctx.command:
        src.reply("已成功取消操作，但若已删除任何数据，则无法恢复！")

@builder.command('!!back clear --confirm')
def on_command_back_clear_confirm(src: CommandSource, ctx: CommandContext):
    if src.is_console:
        src.reply("需指定要操作的玩家，用法：§c!!back clear <player> [--confirm]")
        return
    server = src.get_server().psi()
    uuid = get_uuid(src.player)
    if uuid:
        if rt.cached_positions.get(uuid, None) is not None:
            del rt.cached_positions[uuid]
    else:
        if rt.cached_positions.get(src.player, None) is not None:
            del rt.cached_positions[src.player]
    server.logger.warning(f"玩家{src.player}正在清除其（死亡）数据（1/2）：删除回溯用位置缓存（如有）")
    folder = GetDirectory(TeleportType.Back).private(src.player)
    target_path = os.path.join(folder, "died_history.json")
    if os.path.exists(target_path):
        os.remove(target_path)
        server.logger.warning(f"玩家{src.player}清除了其（死亡）数据（2/2）：{target_path}")
    else:
        server.logger.warning(f"玩家{src.player}清除了其（死亡）数据（2/2）：无历史死亡记录，跳过")
        src.reply("你没有历史死亡记录，将跳过此步骤。")
    on_command_back_clear_cancel(src, ctx)
    src.reply("操作执行完成，您无法再找回已删除的数据！")