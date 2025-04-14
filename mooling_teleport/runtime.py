from mooling_teleport.config import ConfigOptions


config: ConfigOptions = None
init_status = False
do_powerwash = False
clear_back_data = []
cached_positions = {} # 设计为插件卸载时丢失，临时存储玩家执行命令时所在位置，以便回溯