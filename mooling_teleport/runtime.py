from mooling_teleport.config import ConfigOptions


config: ConfigOptions = None
init_status = False
do_powerwash = False
unload_plugin = False
clear_back_data = [] # 临时存储发起删除回溯传送模块中自己数据的玩家列表
cached_positions = {} # 临时存储玩家执行命令时所在位置，以便回溯
tpp_requests = [] # 临时存储玩家间传送的请求列表，以便随时调用