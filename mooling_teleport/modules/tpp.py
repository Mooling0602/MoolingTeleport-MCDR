from mcdreforged.api.all import *


class TeleportPlayer:
    def __init__(self, selected_player: str):
        self.selected_player = selected_player
        self.server = PluginServerInterface

    def execute(self, server: PluginServerInterface, selected: str, target: str):
        server.execute(f"tp {selected} {target}")
        
    def to_another(self, target_player: str):
        self.execute(self.server, self.selected_player, target_player)

    def to_player_here(self, target_player: str):
        self.execute(self.server, target_player, self.selected_player)