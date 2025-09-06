import time
import threading
import mooling_teleport.runtime as rt

from typing import Optional
from mcdreforged.api.all import PluginServerInterface, new_thread
from mooling_teleport.utils import get_time, get_player, check_uuid_valid


lock = threading.Lock()
close_manager = False
server: Optional[PluginServerInterface] = None


def set_server(server_instance: PluginServerInterface):
    global server
    server = server_instance


def stop_manager_thread():
    global close_manager
    close_manager = True
    time.sleep(1)
    close_manager = False
    if not lock.locked():
        server.logger.warning("传送请求管理器线程已被手动退出！")


@new_thread("TimeoutManager(mooling_teleport)")
def manage_tpp_requests():
    while not rt.unload_plugin and close_manager is False:
        with lock:
            now = get_time()
            for i in rt.tpp_requests:
                src = i.src
                if check_uuid_valid(src):
                    src = get_player(src)
                target = i.target
                if check_uuid_valid(target):
                    target = get_player(target)
                if (now - i.time).total_seconds() >= rt.config.tpp_requests_timeout:
                    server.tell(
                        src,
                        f"你发出的传送请求因超时而被删除，若有需要请重新发起！当前传送超时为{rt.config.tpp_requests_timeout}秒钟",
                    )
                    server.tell(
                        target,
                        f"你接受到的传送请求因超时而被删除。当前传送超时为{rt.config.tpp_requests_timeout}秒钟",
                    )
                    rt.tpp_requests.remove(i)
            time.sleep(0.5)
