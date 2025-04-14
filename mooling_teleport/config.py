import os

from mcdreforged.api.all import *


class BackOptions(Serializable):
    max_record: int = 5

class ConfigOptions(Serializable):
    force_rcon: bool = False
    non_vanilla_dim_warning: bool = True
    tpp_requests_timeout: int = 10
    back: BackOptions = BackOptions()

def config_loader(server: PluginServerInterface) -> tuple[bool, ConfigOptions]:
    init_status = False
    config_dir = server.get_data_folder()
    if os.path.exists(os.path.join(config_dir, 'config.yml')) is False:
        init_status = True
        server.logger.warning("主配置不存在，视为初次使用插件！")
    config: ConfigOptions = server.load_config_simple(file_name='config.yml', target_class=ConfigOptions)
    if config.force_rcon is True:
        if server.is_rcon_running() is False:
            server.logger.warning("Rcon不可用！你必须正确配置Rcon，或使用Minecraft Data API！")
            server.logger.info("若服务器还在启动中，请等待其完成。")
            config.force_rcon = False
    return init_status, config
