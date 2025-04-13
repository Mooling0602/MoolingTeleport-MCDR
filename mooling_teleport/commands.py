import ast
import os
import mooling_teleport.runtime as rt

from mcdreforged.api.all import *
from mooling_teleport.utils import StrConverter, enable_force_rcon
from mooling_teleport.help_page import help_info, help_menu, get_back_page
from mooling_teleport.modules.api import TeleportPosition
from mooling_teleport.modules.back import BackTeleport
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
    if rt.do_powerwash is False:
        src.reply("将删除插件主配置，若确定，请再执行一遍指令！")
        src.reply("各种坐标数据将会被保留，如有需要请手动删除！")
        rt.do_powerwash = True
    else:
        do_powerwash()

@builder.command('!!mtp powerwash --confirm')
@builder.command('!!mtp reset config all --confirm')
def do_plugin_powerwash(src: CommandSource, ctx: CommandContext):
    rt.do_powerwash = True
    on_plugin_powerwash(src, ctx)

@builder.command('!!mtp powerwash --cancel')
@builder.command('!!mtp reset config all --cancel')
def cancel_plugin_powerwash(src: CommandSource, ctx: CommandContext):
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

@builder.command('!!back')
@builder.command('!!mooling_teleport:back')
@builder.command('!!back died')
@builder.command('!!mooling_teleport:back died')
def on_command_back_died(src: CommandSource, ctx: CommandContext):
    if not src.is_player:
        src.reply("请以玩家身份运行命令！")
        return
    back = BackTeleport(src.player)
    back.go_to_died_latest()
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
