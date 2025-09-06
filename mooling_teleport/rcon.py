from typing import Optional
from concurrent.futures import ThreadPoolExecutor

server = None


def set_server(server_instance):
    global server
    server = server_instance


def query_rcon_result(command: str) -> str:
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(server.rcon_query, command)
        try:
            result = future.result(timeout=5)
        except TimeoutError:
            # noinspection SpellCheckingInspection
            server.logger.warning("RCON查询超时，需要重建MCDR与服务端之间的连接。")
            try:
                # noinspection PyProtectedMember
                server._mcdr_server.connect_rcon()
                result = future.result(timeout=30)
            except TimeoutError:
                raise TimeoutError("RCON查询长时间无响应！")
    return result


# noinspection SpellCheckingInspection
def get_player_info(player: str, argu: str) -> Optional[list, str]:
    if argu == "Pos":
        resp = query_rcon_result(f"data get entity {player} Pos")
        # resp = "CleMooling has the following entity data: [315.5d, 64.0d, -302.5d]"
        pos = resp.split(":")[1].strip().strip("[]").split(", ")
        position: list = [float(coord[:-1]) for coord in pos]
        return position
    elif argu == "Dimension":
        resp = query_rcon_result(f"data get entity {player} Dimension")
        # resp = "CleMooling has the following entity data: \"minecraft:overworld\""
        dimension = resp.split(": ", 1)[1].strip().strip('"')
        return dimension
    else:
        return None
