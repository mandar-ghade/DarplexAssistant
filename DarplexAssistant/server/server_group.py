from dataclasses import dataclass
from enum import Enum
from pprint import pprint
from typing import Iterator, Optional, Self
from .minecraft_server import MinecraftServer, get_minecraft_servers_by_prefix
from ..repository import get_redis_repo
from ..utils import get_region_by_str, Region


class ServerGroupNotExistsException(Exception):
    pass


def convert_to_str(line: str | int | bool | Region) -> str:
    """Converts data type to string for redis insertion."""
    if isinstance(line, str):
        return line
    elif isinstance(line, bool):
        return str(line).lower()
    elif isinstance(line, int):
        return str(line)
    elif (isinstance(line, Region) or isinstance(line, Enum)):
        return line.value



@dataclass
class ServerGroup:
    prefix: str
    ram: int
    totalServers: int
    joinableServers: int
    portSection: Optional[int]
    arcadeGroup: bool
    worldZip: str
    plugin: str
    configPath: str
    name: str = ''
    host: str = ''
    minPlayers: int = 1
    maxPlayers: int = 50
    pvp: bool = False
    tournament: bool = False
    tournamentPoints: bool = False
    games: str = 'null'
    modes: str = ''
    boosterGroup: str = ''
    serverType: str = 'dedicated'
    addNoCheat: bool = False
    addWorldEdit: bool = False
    teamRejoin: bool = False
    teamAutoJoin: bool = False
    teamForceBalance: bool = False
    gameAutoStart: bool = False
    gameTimeout: bool = False
    gameVoting: bool = False
    mapVoting: bool = False
    rewardGems: bool = False
    rewardItems: bool = False
    rewardStats: bool = False
    rewardAchievements: bool = False
    hotbarInventory: bool = False
    hotbarHubClock: bool = False
    playerKickIdle: bool = False
    hardMaxPlayerCap: bool = False
    staffOnly: bool = False
    whitelist: bool = False
    resourcePack: str = '' 
    region: Region = Region.US
    teamServerKey: str = ''
    portalBottomCornerLocation: str = ''
    portalTopCornerLocation: str = '' 
    npcName: str = ''
    cpu: int = 1

    def _exists(self) -> bool:
        """Returns if ServerGroup exists in Redis DB."""
        with get_redis_repo() as repository:
            return repository.server_group_exists(self.prefix) 

    def __post_init__(self) -> None:
        if self._exists():
            for key, value in self.parameterize_server_group_dict(self.prefix).items():
                setattr(self, key, value)
        with get_redis_repo() as repo:
            if self.portSection is None or (not self._exists and repo.get_if_port_conflicts(self.portSection)):
                self.portSection = repo.next_available_port()
        self._servers = self.servers

    @property
    def servers(self) -> Iterator[MinecraftServer]:
        yield from filter(lambda server: server.exists,
                          get_minecraft_servers_by_prefix(self.prefix, self.region))

    def _convert_to_dict(self) -> dict[str, str]:
        """Converts ServerGroup object to dictionary."""
        return dict((key, convert_to_str(val)) for key, val in self.__dict__.items() if key != '_servers')

    def get_create_cmd(self, server_num: int) -> str:
        """Gets create server command for the `startServer.py` script"""
        assert isinstance(self.portSection, int)
        return (f'python3 startServer.py 127.0.0.1 127.0.0.1 {self.portSection + server_num}'
                f' {self.ram}'
                f' {self.worldZip}'
                f' {self.plugin}'
                f' {self.configPath}'
                f' {self.prefix}'
                f' {self.prefix}-{server_num}'
                f' {convert_to_str(self.region in (Region.US, Region.ALL))}'
                f' {convert_to_str(self.addNoCheat)}'
                f' {convert_to_str(self.addWorldEdit)}')

    def get_delete_cmd(self, server_num: int) -> str:
        """Gets delete server command for the `stopServer.py` script"""
        return f'python3 stopServer.py 127.0.0.1 {self.prefix}-{server_num}'

    def is_player_server(self) -> bool:
        """Returns `True` if `ServerGroup` is an MPS (Multiplayer Private Server) ServerGroup."""
        return self.serverType == 'Player'

    def is_event_server(self) -> bool:
        """Returns `True` if `ServerGroup` is a COM (Community) ServerGroup"""
        return self.serverType == 'Community'

    def increment_total_servers(self) -> None:
        """Increments `totalServers` by one.
        (Internal method)."""
        # TODO: Fix for Lobby creation
        with get_redis_repo() as repo:
            repo.redis.hset(f'servergroups.{self.prefix}', 'totalServers', f'{self.totalServers+1}')
            self.totalServers += 1

    def decrement_total_servers(self) -> None:
        """Decrements `totalServers` by one. (`totalServers` >= 0).
        (Internal method)."""
        with get_redis_repo() as repo:
            if self.totalServers - 1 < 0:
                return
            repo.redis.hset(f'servergroups.{self.prefix}', 'totalServers', f'{self.totalServers-1}')
            self.totalServers -= 1

    def set_total_servers(self, count: int) -> None:
        """Set totalServers to specified `count`"""
        with get_redis_repo() as repo:
            repo.redis.hset(f'servergroups.{self.prefix}', 'totalServers', f'{count}')

    def deploy_minecraft_servers(self, count: int) -> None:
        """Creates `count` number of `MinecraftServer`s.
        Check `RedisRepository`.`server_group_exists` before expecting new instances"""
        for _ in range(count):
            self.increment_total_servers()

    def remove_minecraft_servers(self, count: int) -> None:
        """Deletes `count` number of `MinecraftServer`s.
        Will only work if server group exists in Redis.
        (Check with `RedisRepository`'s `server_group_exists`).
        """
        for _ in range(count):
            self.decrement_total_servers()

    def create(self) -> None:
        """Creates the ServerGroup key in Redis.
        Only creates key if not exists. 
        Does not rewrite data.

        Can also be used within GameOptions module.
        Proper usage:

        >>> from DarplexAssistant import GameOptions
        >>> server_group = GameOptions.convert_from_game(GameOptions.Micro)._convert_to_server_group()
        ServerGroup
        >>> server_group.delete()
        None
        """
        with get_redis_repo() as repo:
            while self.portSection is None or (not self._exists() and repo.get_if_port_conflicts(self.portSection)):
                self.portSection = repo.generate_random_port()
            repo.create_server_group(self.prefix, self._convert_to_dict())

    def overwrite(self) -> None:
        """Recreates Redis ServerGroup."""
        with get_redis_repo() as repo:
            if repo.server_group_exists(self.prefix):
                self.delete()
            self.create()

    def delete(self) -> None:
        """Deletes the ServerGroup key in Redis.
        Only deletes key if exists. 
        Does not rewrite data.

        Can also be used with GameOptions module.
        Proper usage:

        >>> from DarplexAssistant import GameOptions
        
        >>> server_group = GameOptions.convert_from_game(GameOptions.Micro)._convert_to_server_group()
        ServerGroup
        >>> server_group.delete()

        None
        """
        with get_redis_repo() as repo:
            repo.delete_server_group(self.prefix)

    @staticmethod
    def parameterize_server_group_dict(prefix: str) -> dict[str, str | int | Region | bool]:
        with get_redis_repo() as repository:
            data = repository.get_server_group_dict(prefix).copy()
        return dict(
            prefix = data.get('prefix', ''),
            ram = int(data.get('ram', 512)),
            totalServers = int(data.get('totalServers', 0)),
            joinableServers = int(data.get('joinableServers', 0)),
            portSection = int(data.get('portSection', repository.next_available_port())),
            arcadeGroup = data.get('arcadeGroup') == 'true',
            worldZip = data.get('worldZip', 'lobby.zip'),
            plugin = data.get('plugin', 'Hub.jar'),
            configPath = data.get('configPath', 'plugins/Hub'),
            name = data.get('name', data.get('prefix', '')),
            host = data.get('host', ''),
            minPlayers = int(data.get('minPlayers', 1)),
            maxPlayers = int(data.get('maxPlayers', 50)),
            pvp = data.get('pvp') == 'true',
            tournament = data.get('tournament') == 'true',
            tournamentPoints = data.get('tournamentPoints') == 'true',
            games = data.get('games', 'null'),
            modes = data.get('modes', ''),
            boosterGroup = data.get('boosterGroup', ''),
            serverType = data.get('serverType', 'dedicated'), 
            addNoCheat = data.get('addNoCheat', 'true') == 'true', 
            addWorldEdit = data.get('addWorldEdit') == 'true',
            teamRejoin = data.get('teamRejoin') == 'true',
            teamAutoJoin = data.get('teamAutoJoin') == 'true',
            teamForceBalance = data.get('teamForceBalance') == 'true',
            gameAutoStart = data.get('gameAutoStart') == 'true',
            gameTimeout = data.get('gameTimeout') == 'true',
            gameVoting = data.get('gameVoting')  == 'true',
            mapVoting = data.get('mapVoting') == 'true',
            rewardGems = data.get('rewardGems') == 'true',
            rewardItems = data.get('rewardItems') == 'true',
            rewardStats = data.get('rewardStats') == 'true', 
            rewardAchievements = data.get('rewardAchievements') == 'true',
            hotbarInventory = data.get('hotbarInventory') == 'true',
            hotbarHubClock = data.get('hotbarHubClock') == 'true', 
            playerKickIdle = data.get('playerKickIdle') == 'true',
            hardMaxPlayerCap = data.get('hardMaxPlayerCap') == 'true',
            staffOnly = data.get('staffOnly') == 'true', 
            whitelist = data.get('whitelist') == 'true', 
            resourcePack = data.get('resourcePack', ''),
            region = get_region_by_str(data.get('region', '')), # defaults to US anyways
            teamServerKey = data.get('teamServerKey', ''),
            portalBottomCornerLocation = data.get('portalBottomCornerLocation', ''),
            portalTopCornerLocation = data.get('portalTopCornerLocation', ''),
            npcName = data.get('npcName', ''),
            cpu = int(data.get('cpu', 1))
        )

    def __hash__(self) -> int:
        return hash(self.prefix)

    def __eq__(self, other: object) -> bool:
        return hash(self) == hash(other)

    @classmethod
    def convert_to_server_group(cls, prefix: str) -> Self:
        """Converts to ServerGroup object from prefix (if it exists in redis).
        If ServerGroup not found, raises `ServerGroupNotExistsException`.
        """
        return cls(**ServerGroup.parameterize_server_group_dict(prefix)) # type: ignore

