from dataclasses import dataclass
import json
import time
from typing import Iterator, Optional, Self
from GameJoinStatus import GameJoinStatus
from GameStatusDisplay import GameStatusDisplay

from RedisAssistant import RedisAssistant

class MinecraftServerNotExistsException(Exception):
    pass

@dataclass
class MinecraftServer:
    name: str
    group: str
    motd: str
    player_count: int
    max_player_count: int
    tps: int
    ram: int
    max_ram: int
    public_address: str
    port: int
    donors_online: int
    start_up_date: int
    current_time: int
    is_online: bool = False
    game: Optional[str] = None
    mode: Optional[str] = None
    status: Optional[GameStatusDisplay] = None
    joinable: Optional[GameJoinStatus] = None

    def __post_init__(self) -> None:
        self.is_online = (time.time() * 1000 - self.current_time) <= 10000
        if self.motd == 'A Minecraft Server':
            return
        motd_json = json.loads(self.motd)
        self.game = motd_json.get('_game')
        self.mode = motd_json.get('_mode')
        self.status = GameStatusDisplay(motd_json.get('_status'))
        self.joinable = GameJoinStatus(motd_json.get('_joinable'))

    def _needs_restart(self) -> bool:
        return self.is_online and ('Restarting' in self.motd or 'Finished' in self.motd)
    
    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self: Self, other) -> bool:
        if not isinstance(other, Self):
            return False
        return hash(self) == hash(other)

    @classmethod
    def convert_to_minecraft_server(cls, server: str) -> Self:
        ra = RedisAssistant.create_session()
        ss_name = f'serverstatus.minecraft.US.{server}'
        ss = ra.redis.get(ss_name)
        if ss is None:
            raise MinecraftServerNotExistsException 
        ss = json.loads(str(ss))
        ra.redis.close()
        return cls(
            name = ss.get('_name'),
            group = ss.get('_group'),
            motd = ss.get('_motd'),
            player_count = int(ss.get('_playerCount')),
            max_player_count = int(ss.get('_maxPlayerCount')),
            tps = int(ss.get('_tps')),
            ram = int(ss.get('_ram')),
            max_ram = int(ss.get('_maxRam')),
            public_address = ss.get('_publicAddress'),
            port = int(ss.get('_port')),
            donors_online = int(ss.get('_donorsOnline')),
            start_up_date = int(ss.get('_startUpDate')),
            current_time = int(ss.get('_currentTime'))
        )

def get_minecraft_servers_by_prefix(prefix: str) -> Iterator[MinecraftServer]:
    ra = RedisAssistant.create_session()
    for group in ra.redis.scan_iter(f'serverstatus.minecraft.US.{prefix}-*'):
        group_name = group.strip('serverstatus.minecraft.US.')
        yield MinecraftServer.convert_to_minecraft_server(group_name)
    ra.redis.close()

