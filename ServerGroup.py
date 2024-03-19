from dataclasses import dataclass
from RedisAssistant import RedisAssistant
from Region import Region

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
    resourcePack: str = '' #unused
    region: Region = Region.US
    teamServerKey: str = ''
    portalBottomCornerLocation: str = '' #unused
    portalTopCornerLocation: str = '' #unused
    npcName: str = ''
    cpu: int = 1

    def _convert_to_dict(self) -> dict[str, str]:
        """Converts ServerGroup object to dictionary."""
        return dict((key, convert_to_str(val)) for key, val in self.__dict__.items())

    def get_create_cmd(self, server_num: int) -> str:
        return (f'python3 startServer.py 127.0.0.1 127.0.0.1 {self.portSection}'
                f' {self.ram}'
                f' {self.worldZip}'
                f' {self.plugin}'
                f' {self.configPath}'
                f' {self.prefix}'
                f' {self.prefix}-{server_num}'
                f' {convert_to_str(self.region == Region.US)}'
                f' {convert_to_str(self.addNoCheat)}'
                f' {convert_to_str(self.addWorldEdit)}')

    def _create(self) -> None:
        """
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

    def _delete(self) -> None:
        """
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

