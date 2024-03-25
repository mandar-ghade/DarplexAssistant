from dataclasses import dataclass
from typing import Iterator, Optional, Self
from MinecraftServer import MinecraftServer, get_minecraft_servers_by_prefix
from RedisAssistant import RedisAssistant
from Region import Region
from redis_utils import get_region_by_str


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
    elif isinstance(line, Region):
        return line.value



@dataclass
class ServerGroup:
    prefix: str
    ram: int
    totalServers: int
    joinableServers: int
    portSection: int
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
    servers: Iterator[MinecraftServer] = iter([])

    def _exists(self) -> bool:
        """Returns if ServerGroup exists in Redis DB."""
        ra = RedisAssistant.create_session()
        exists = ra.redis.hgetall(f'servergroups.{self.prefix}') is not None
        ra.redis.close()
        return exists

    def __post_init__(self) -> None:
        self._update_servers()

    # Run this every few seconds in the monitor.
    def _update_servers(self) -> None:
        """Updates Minecraft Servers."""
        servers = list(get_minecraft_servers_by_prefix(self.prefix))
        self.servers = iter(list(filter(lambda server: server.exists, servers)))

    def _convert_to_dict(self) -> dict[str, str]:
        """Converts ServerGroup object to dictionary."""
        return dict((key, convert_to_str(val)) for key, val in self.__dict__.items())

    def get_create_cmd(self, server_num: int) -> str:
        return (f'python3 startServer.py 127.0.0.1 127.0.0.1 {self.portSection + server_num}'
                f' {self.ram}'
                f' {self.worldZip}'
                f' {self.plugin}'
                f' {self.configPath}'
                f' {self.prefix}'
                f' {self.prefix}-{server_num}'
                f' {convert_to_str(self.region == Region.US)}'
                f' {convert_to_str(self.addNoCheat)}'
                f' {convert_to_str(self.addWorldEdit)}')

    def get_delete_cmd(self, server_num: int) -> str:
        return f'python3 stopServer.py 127.0.0.1 {self.prefix}-{server_num}'

    def deploy(self, server_id: int) -> None:
        """Deploys server."""
        pass

    def kill(self, server_id: int) -> None:
        """Kills server."""
        pass

    def _create(self) -> None:
        """
        (Do not use this method.
        Direct implementation and proper usage is shown below)
        
        Creates the ServerGroup key in Redis.
        Only creates key if not exists. 
        Does not rewrite data.

        Use with ServerType and GameType modules.
        
        >>> from ServerType import ServerType
        >>> from GameType import GameType

        >>> ServerType(GameType.Micro).options._convert_to_server_group().create()
        None
        
        Proper usage:

        >>> from ServerType import ServerType
        >>> from GameType import GameType
        
        >>> ServerType(GameType.Micro).create()
        None

        """
        ra = RedisAssistant.create_session()
        if ra.server_group_exists(self.prefix):
            return
        ra.redis.sadd('servergroups', self.prefix)
        ra.redis.hmset(f'servergroups.{self.prefix}', self._convert_to_dict())
        ra.redis.close()
    
    def _overwrite(self) -> None:
        """
        Recreates Redis ServerGruop.
        """
        ra = RedisAssistant.create_session()
        if ra.server_group_exists(self.prefix):
            self._delete()
        self._create()
        ra.redis.close()

    def _delete(self) -> None:
        """
        (Do not use this method.
        Direct implementation and proper usage is shown below)

        Creates the ServerGroup key in Redis.
        Only creates key if not exists. 
        Does not rewrite data.

        Use with Game module.
        
        >>> from ServerType import ServerType
        >>> from GameType import GameType

        >>> ServerType(GameType.Micro).options._convert_to_server_group().delete()
        None
        
        Proper usage:

        >>> from ServerType import ServerType
        >>> from GameType import GameType
        
        >>> ServerType(GameType.Micro).delete()
        None

        """
        ra = RedisAssistant.create_session()
        if not ra.server_group_exists(self.prefix):
            return
        ra.redis.srem('servergroups', self.prefix)
        ra.redis.delete(f'servergroups.{self.prefix}')
        ra.redis.close()

    @classmethod
    def convert_to_server_group(cls, prefix: str) -> Self:
        """Converts to ServerGroup object from prefix (if it exists in redis)."""
        ra = RedisAssistant.create_session()
        next_port = ra.next_available_port()
        data: Optional[dict[str, str]] = ra.redis.hgetall(f'servergroups.{prefix}')
        if data is None:
            raise ServerGroupNotExistsException
        ra.redis.close()
        return cls(
            prefix = data.get('prefix', ''),
            ram = int(data.get('ram', 512)),
            totalServers = int(data.get('totalServers', 0)),
            joinableServers = int(data.get('joinableServers', 0)),
            portSection = int(data.get('portSection', next_port)),
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
            region = get_region_by_str(data.get('region', '')),
            teamServerKey = data.get('teamServerKey', ''),
            portalBottomCornerLocation = data.get('portalBottomCornerLocation', ''),
            portalTopCornerLocation = data.get('portalTopCornerLocation', ''),
            npcName = data.get('npcName', ''),
            cpu = int(data.get('cpu', 1))
        )

