import os
import mooling_teleport.runtime as rt

from mcdreforged.api.all import *
from datetime import datetime
from mooling_teleport.utils import StrConverter, enable_force_rcon, get_uuid, check_uuid_valid, get_player, get_nested_keys
from mooling_teleport.help_page import help_info, help_menu, get_back_page, get_warp_page
from mooling_teleport.modules.api import TeleportPosition, TeleportType, Player
from mooling_teleport.modules.back import BackTeleport, cache_position
from mooling_teleport.modules.storage import GetDirectory
from mooling_teleport.modules.tpp import TeleportPlayer
from mooling_teleport.modules.warp_with_loc import LocationMarkerTeleport
from mooling_teleport.utils import format_time, change_config_and_save, get_pfxed_message
from mooling_teleport.task import lock, manage_tpp_requests, stop_manager_thread

psi = ServerInterface.psi()
builder = SimpleCommandBuilder()


def command_register(server: PluginServerInterface):
    builder.arg('num', Integer)
    builder.arg('option', Text).suggests(lambda: get_nested_keys(rt.config))
    builder.arg('value', Text)
    builder.arg('player', Text)
    builder.arg('name', Text)
    builder.register(server)

@builder.command('!!mtp')
def on_command_plg_main(src: CommandSource, ctx: CommandContext):
    src.reply(help_info)

@builder.command('!!mtp help')
def on_command_help_menu(src: CommandSource, ctx: CommandContext):
    src.reply(help_menu)

@builder.command('!!mtp help back')
@builder.command('!!back help')
@builder.command('!!mooling_teleport:back help')
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

@builder.command('!!mtp debug tpp print_requests')
def on_debug_tpp_requests(src: CommandSource, ctx: CommandContext):
    src.reply(rt.tpp_requests)

@builder.command('!!mtp debug tpp request_manager')
@builder.command('!!mtp debug tpp request_manager status')
def on_debug_tpp_request_manager(src: CommandSource, ctx: CommandContext):
    if lock.locked():
        src.reply("请求管理器正在运行")
    else:
        src.reply("请求管理器未在运行，超时将不会发生，直至插件被卸载！")

@builder.command('!!mtp debug tpp request_manager start')
def on_debug_tpp_request_manager_start(src: CommandSource, ctx: CommandContext):
    if not src.has_permission_higher_than(3):
        src.reply("权限不足！")
        return
    if not lock.locked():
        manage_tpp_requests()
        src.reply("已启动请求管理器！")
    else:
        src.reply("请求管理器已在运行！")

@builder.command('!!mtp debug tpp request_manager stop')
def on_debug_tpp_request_manager_stop(src: CommandSource, ctx: CommandContext):
    if not src.has_permission_higher_than(3):
        src.reply("权限不足！")
        return
    if lock.locked():
        stop_manager_thread()
        src.reply("正在关闭请求管理器……")
    else:
        src.reply("请求管理器未在运行！")

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
def on_command_back_main(src: CommandSource, ctx: CommandContext):
    if not src.is_player:
        src.reply(get_back_page(src))
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

# 玩家间传送主命令
@builder.command('!!tpp')
@builder.command('!!mooling_teleport:tpp')
@builder.command('!!tpp help')
@builder.command('!!mooling_teleport:tpp help')
def on_command_tpp_main(src: CommandSource, ctx: CommandContext):
    src.reply("帮助页暂未完成……")

@builder.command('!!tpp accept')
def on_command_tpp_accept(src: CommandSource, ctx: CommandContext):
    if not src.is_player:
        src.reply("该命令只能由玩家执行！")
        return
    teleported = False
    target_request = None
    target = None
    for i in rt.tpp_requests:
        if check_uuid_valid(i.target):
            target = Player.by_uuid(i.target)
        else:
            target = Player.by_name(i.target)
        player = Player.by_name(src.player)
        if target == player:
            target_request = i
            if not i.reverse:
                src.reply("你同意了一个传送到你所在位置的请求，正在执行传送……")
                TeleportPlayer(i.src).to_another(src.player)
                src.reply(f"已将玩家{i.src}传送到你所在位置！")
                teleported = True
            else:
                src.reply("你同意了一个将你传送到对方所在位置的请求，正在执行传送……")
                TeleportPlayer(i.src).to_player_here(src.player)
                src.reply(f"已将你传送到玩家{i.src}所在位置！")
                teleported = True
    if teleported:
        rt.tpp_requests.remove(target_request)
    else:
        src.reply("没有待处理的传送请求（你不能同意自己发出的请求）！")

@builder.command('!!tpp reject')
def on_command_tpp_reject(src: CommandSource, ctx: CommandContext):
    if not src.is_player:
        src.reply("该命令只能由玩家执行！")
        return
    rejected = False
    target = None
    for i in rt.tpp_requests:
        if check_uuid_valid(i.target):
            target = Player.by_uuid(i.target)
        else:
            target = Player.by_name(i.target)
        player = Player.by_name(src.player)
        if target == player:
            source = i.src
            if check_uuid_valid(source):
                source = get_player(source)
            rt.tpp_requests.remove(i)
            src.reply(f"你拒绝了来自玩家{source}的传送请求！")
            rejected = True
    if not rejected:
        src.reply("你没有待处理的传送请求（你不能拒绝自己发出的请求，而应该取消它）！")

@builder.command('!!tpp cancel')
def on_command_tpp_cancel(src: CommandSource, ctx: CommandContext):
    if not src.is_player:
        src.reply("该命令只能由玩家执行！")
        return
    cancelled = False
    source = None
    for i in rt.tpp_requests:
        if check_uuid_valid(i.src):
            source = Player.by_uuid(i.src)
        else:
            source = Player.by_name(i.src)
        player = Player.by_name(src.player)
        if source == player:
            target = i.target
            if check_uuid_valid(target):
                target = get_player(target)
            rt.tpp_requests.remove(i)
            src.reply(f"你已取消发送给玩家{target}的传送请求！")
            cancelled = True
    if not cancelled:
        src.reply("你没有可以取消的传送请求！")

@builder.command('!!tpa')
@builder.command('!!tpa help')
def on_command_tpa_main(src: CommandSource, ctx: CommandContext):
    src.reply("帮助页尚未完成……")

@builder.command('!!tpa <player>')
def on_command_tpa_player(src: CommandSource, ctx: CommandContext):
    if not src.is_player:
        src.reply("该命令只能由玩家执行！")
        return
    server = src.get_server().psi()
    TeleportPlayer(src.player).send_request(ctx['player'])
    server.tell(ctx['player'], f"[玩家间传送] 玩家{src.player}想要传送到你所处的位置！")
    src.reply(f"已向玩家{ctx['player']}发送传送请求，对方通过后将把你传送至其所在位置。")
    src.reply("请注意，在你等待请求被同意的期间，对方的位置可能会有变化。")

@builder.command('!!tph <player>')
@builder.command('!!tpahere <player>')
def on_command_tph_player(src: CommandSource, ctx: CommandContext):
    if not src.is_player:
        src.reply("该命令只能由玩家执行！")
        return
    server = src.get_server().psi()
    TeleportPlayer(src.player).send_request(ctx['player'], True)
    server.tell(ctx['player'], f"[玩家间传送] 玩家{src.player}想要把你传送到其所处的位置！")
    src.reply(f"已向玩家{ctx['player']}发送传送请求，对方通过后将被传送至你所在位置。")
    src.reply("请注意不要离开你现在所处范围太远，对方无法预期你的位置变化！")

@builder.command('!!warp')
@builder.command('!!warp help')
def on_command_warp(src: CommandSource, ctx: CommandContext):
    src.reply(get_warp_page())

@builder.command('!!warp list')
def on_command_warp_list(src: CommandSource, ctx: CommandContext):
    src.reply("下面是LocationMarker的所有路标（名称）：")
    try:
        locnames = LocationMarkerTeleport().get_locname_list()
        for i in locnames:
            src.reply(f"- {i}")
    except Exception as e:
        src.reply("读取时发生错误：")
        src.reply(e)

@builder.command('!!warp <name>')
def on_command_warp_name(src: CommandSource, ctx: CommandContext):
    if not src.is_player:
        src.reply("该命令只能由玩家执行！")
        return
    location = LocationMarkerTeleport().get_location(ctx['name'])
    if location is not None:
        src.reply(get_pfxed_message("该路标点存在，正在将你传送至指定位置……"))
        position = location.position
        TeleportPosition().by_class_position(position, src.player)
        src.reply(get_pfxed_message("传送执行完成！"))
