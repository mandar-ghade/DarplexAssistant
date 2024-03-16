from dataclasses import dataclass
from Region import Region
from pprint import pprint

from redis_utils import GAMEMODES_TO_GAME_DISPLAY, REDIS_KEYS_TO_GAME_DISPLAY, TEAM_SERVER_KEYS, npc_name_from_prefix

@dataclass
class ServerGroup:
    prefix: str 
    host: str
    ram: int
    totalServers: int
    joinableServers: int
    portSection: int
    arcadeGroup: bool
    worldZip: str
    plugin: str
    configPath: str
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
    
    def __post_init__(self):
        self.region = self.region.value
        if self.arcadeGroup and self.serverType != 'PLAYER':
            self.serverType = 'Minigames'
        self.teamServerKey = TEAM_SERVER_KEYS.get(self.prefix, '')
        self.npcName = npc_name_from_prefix(self.prefix)
        if self.prefix == 'MIN':
            self.games = 'BaconBrawl,Lobbers,DeathTag,DragonEscape,Dragons,Evolution,Micro,MilkCow,Paintball,Quiver,Runner,Sheep,Snake,SneakyAssassins,Spleef,SquidShooter,TurfWars,WitherAssault'
        else:
            self.games = REDIS_KEYS_TO_GAME_DISPLAY.get(self.prefix, GAMEMODES_TO_GAME_DISPLAY.get(self.npcName, 'null'))


sg = ServerGroup('CW4', 'Lobby-1', 512, 0, 0, 25701, False, 'Lobby.zip', 'lobby.jar', '/plugins/Hub')

print(sg.__dict__.keys())
pprint(sg, width=20)
