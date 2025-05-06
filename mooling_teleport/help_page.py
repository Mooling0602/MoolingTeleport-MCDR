from mcdreforged.api.all import *


help_info = RTextList(
    RText("§7!!mtp §r插件主命令，显示最基本的帮助信息") + "\n",
    RText("§7!!mtp help [<module>] §r插件帮助中心，显示帮助页目录或具体模块详情")
)

help_menu = RTextList(
    RText("# [木泠牌传送] 插件帮助中心") + "\n",
    RText("§7!!mtp help <module>§r 查看查看指定模块的帮助") + "\n",
    RText("## 可用的功能性模块列表") + "\n",
    RText("- §eback §r查看回溯传送相关的命令用法") + "\n",
    RText("## 可用的调试性模块列表") + "\n",
    RText("- §edebug §r查看调试命令主要用法") + "\n",
    RText("- §eset config §r查看修改插件配置的用法") + "\n",
    RText("- §ereset config §r查看重置插件配置的用法") + "\n",
    RText("§7  使用§r§c!!mtp powerwash§r或§c!!mtp reset config all§r§7以重置所有插件配置项，不影响命令注册相关配置§r")
)

class back_message_main(Serializable):
    console: str = "玩家执行后，可返回其传送前所在或上次死亡的地点"
    player: str = "返回你传送前所在或上次死亡的地点，前者将在此命令提交后刷新"

class back_message_died(Serializable):
    console: str = "玩家执行后，返回其上次死亡的地点"
    player: str = "返回你上次死亡的地点，加上整数可指定要返回到的记录"

class back_message_died_list(Serializable):
    console: str = "玩家执行后，向其显示其所有死亡记录"
    player: str = "显示你的历史死亡记录"

def get_back_page(src: CommandSource) -> RTextList:
    message_main = back_message_main.player if src.is_player else back_message_main.console
    message_died = back_message_died.player if src.is_player else back_message_died.console
    message_died_list = back_message_died_list.player if src.is_player else back_message_died_list.console
    back_page = RTextList(
        RText("# [木泠牌传送] 回溯传送帮助信息") + "\n",
        RText(f"§7!!back §r{message_main}") + "\n",
        RText(f"§7!!back died [<num>] §r{message_died}") + "\n",
        RText(f"§7!!back died list §r{message_died_list}")
    )
    return back_page

def get_warp_page() -> RTextList:
    warp_page = RTextList(
        RText("# [木泠牌传送] 公共传送帮助信息") + "\n",
        RText("§7!!warp [help] §r显示此帮助页面") + "\n",
        RText("§7!!warp <name> §r传送到指定的路标点") + "\n",
        RText("§7!!warp list §r显示所有路标（仅名称）") + "\n",
        RText("[!] 目前数据源仅对接了LocationMarker，需要更多功能可以直接使用该插件的命令！")
    )
    return warp_page