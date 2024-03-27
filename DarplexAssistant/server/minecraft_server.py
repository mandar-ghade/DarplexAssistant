from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from typing import Iterator, Optional, Self

from ..repository import RedisRepository
from ..utils import GameJoinStatus, GameStatusDisplay, Region


class MinecraftServerNotExistsException(Exception):
    pass


def get_minecraft_server_json_value(server_name: str, key: str) -> str:
    ra = RedisRepository.create_session()
    resp = ra.redis.get(f'serverstatus.minecraft.US.{server_name}')
    if resp is None:
        return '-1'
    resp = json.loads(str(resp))
    ra.redis.close()
    return resp.get(key, '-1')


def get_attribute_by_motd(motd: str, attribute: str) -> Optional[str]:
    if motd in ('A Minecraft Server', '-1'):
        return 
    motd_json = json.loads(motd)
    if attribute not in ('_game', '_mode', '_status', '_joinable'):
        return
    return motd_json.get(attribute)


def get_if_exists(server_name: str) -> bool:
    r = RedisRepository.create_session()
    exists = r.redis.get(f'serverstatus.minecraft.US.{server_name}') is not None
    r.redis.close()
    return exists


@dataclass
class MinecraftServer:
    name: str
    _group: str = ''
    _max_ram: int = 0
    _public_address: str = ''
    _port: int = 0
    _start_up_date: Optional[datetime] = None
    _motd: str = ''
    _player_count: int = 0
    _max_player_count: int = 0
    _tps: int = 0
    _ram: int = 0
    _donors_online: int = 0
    _current_time: Optional[datetime] = None
    _is_online: bool = False
    _uptime: Optional[timedelta] = None
    _game: Optional[str] = None
    _mode: Optional[str] = None
    _status: Optional[GameStatusDisplay] = None
    _joinable: Optional[GameJoinStatus] = None
    _exists: bool = False

    def __post_init__(self) -> None:
        self._group = self.name.split('-')[0]
        self._max_ram = self.max_ram
        self._public_address = self.public_address
        self._port = self.port
        self._start_up_date = self.start_up_date
        self._motd = self.motd
        self._player_count = self.player_count
        self._max_player_count = self.max_player_count
        self._tps = self.tps
        self._ram = self.ram
        self._donors_online = self.donors_online
        self._current_time = self.current_time
        self._is_online = self.is_online
        self._uptime = self.uptime
        self._game = self.game
        self._mode = self.mode
        self._status = self.status
        self._joinable = self.joinable
        self._exists = self._exists

    @property
    def group(self) -> str:
        self._group = self.name.split('-')[0]
        return self._group

    @property
    def max_ram(self) -> int:
        self._max_ram = int(get_minecraft_server_json_value(self.name, '_maxRam'))
        return self._max_ram

    @property
    def public_address(self) -> str:
        self._public_address = get_minecraft_server_json_value(self.name, '_publicAddress')
        return self._public_address

    @property
    def port(self) -> int:
        self._port = int(get_minecraft_server_json_value(self.name, '_port'))
        return self._port

    @property
    def start_up_date(self) -> Optional[datetime]:
        if not self.exists:
            return None
        self._start_up_date = datetime.fromtimestamp(int(get_minecraft_server_json_value(self.name, '_startUpDate')))
        return self._start_up_date # .strftime("%Y-%m-%d %H:%M:%S")

    @property
    def motd(self) -> str:
        self._motd = get_minecraft_server_json_value(self.name, '_motd')
        return self._motd

    @property
    def player_count(self) -> int:
        self._player_count = int(get_minecraft_server_json_value(self.name, '_playerCount'))
        return self._player_count

    @property
    def max_player_count(self) -> int:
        self._max_player_count = int(get_minecraft_server_json_value(self.name, '_maxPlayerCount'))
        return self._max_player_count

    @property
    def tps(self) -> int:
        self._tps = int(get_minecraft_server_json_value(self.name, '_tps'))
        return self._tps

    @property
    def ram(self) -> int:
        self._ram = int(get_minecraft_server_json_value(self.name, '_ram'))
        return self._ram

    @property
    def donors_online(self) -> int:
        self._donors_online = int(get_minecraft_server_json_value(self.name, '_donorsOnline'))
        return self._donors_online

    @property
    def current_time(self) -> Optional[datetime]:
        if not self.exists:
            return None 
        self._current_time = datetime.fromtimestamp(int(get_minecraft_server_json_value(self.name, '_currentTime')) / 1000)
        return self._current_time

    @property
    def is_online(self) -> bool:
        if not self.current_time:
            return False
        self._is_online = datetime.now().timestamp() - self.current_time.timestamp() <= 10000 
        return self._is_online

    @property
    def uptime(self) -> Optional[timedelta]:
        if not self.current_time or not self.start_up_date:
            return None
        return self.current_time - self.start_up_date

    @property
    def game(self) -> Optional[str]:
        self._game = get_attribute_by_motd(self.motd, '_game')
        return self._game

    @property
    def mode(self) -> Optional[str]:
        self._mode = get_attribute_by_motd(self.motd, '_mode')
        return self._mode

    @property
    def status(self) -> Optional[GameStatusDisplay]:
        self._status = None if self.motd in ('A Minecraft Server', '-1') else GameStatusDisplay(get_attribute_by_motd(self.motd, '_status'))
        return self._status

    @property
    def joinable(self) -> Optional[GameJoinStatus]:
        self._joinable = None if self.motd in ('A Minecraft Server', '-1') else GameJoinStatus(get_attribute_by_motd(self.motd, '_joinable'))
        return self._joinable

    @property
    def exists(self) -> bool:
        self._exists = get_if_exists(self.name)
        return self._exists

    def get_create_cmd(self) -> str:
        ra = RedisRepository.create_session()
        if not ra.server_group_exists(self.group): # just in case 
            return ''
        data: dict[str, str] = json.loads(str(ra.redis.hgetall(f'servergroups.{self.group}')).replace("'", '"'))
        output = (f'python3 startServer.py 127.0.0.1 127.0.0.1 {self.port}'
                  f' {self.max_ram}'
                  f' {data.get("worldZip")}'
                  f' {data.get("plugin")}'
                  f' {data.get("configPath")}'
                  f' {self.group}'
                  f' {self.name}'
                  f' {str(data.get("region", "US") == "US").lower()}'
                  f' {str(data.get("addNoCheat") == "true").lower()}'
                  f' {str(data.get("addWorldEdit") == "true").lower()}')
        ra.redis.close()
        return output

    def get_delete_cmd(self) -> str:
        return f'python3 stopServer.py 127.0.0.1 {self.name}'
    
    def _needs_restart(self) -> bool:
        return self.is_online and ('Restarting' in self.motd 
                                   or 'Finished' in self.motd)

    def __hash__(self) -> int:
        return hash(self.name)

    def __eq__(self: Self, other) -> bool:
        if not isinstance(other, Self):
            return False
        return hash(self) == hash(other)

    @classmethod
    def convert_to_minecraft_server(cls, server: str) -> Self:
        """
        Converts to `MinecraftServer` from existing ServerStatus cache.
        Will return `MinecraftServerNotExistsException` if DNE.

        """
        repository = RedisRepository.create_session()
        minecraft_server = repository.get_server_status_dict(server, Region.US)
        repository.close_connection()
        name: Optional[str] = None
        if minecraft_server is None:
            raise MinecraftServerNotExistsException
        elif (name := minecraft_server.get('_name')) is None:
            raise MinecraftServerNotExistsException
        return cls(
            name = name
        )


def get_minecraft_servers_by_prefix(prefix: str) -> Iterator[MinecraftServer]:
    ra = RedisRepository.create_session()
    for group in ra.redis.scan_iter(f'serverstatus.minecraft.US.{prefix}-*'):
        group_name: str = group.replace('serverstatus.minecraft.US.', '')
        yield MinecraftServer.convert_to_minecraft_server(group_name)
    ra.redis.close()

