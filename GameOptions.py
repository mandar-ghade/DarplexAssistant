
from dataclasses import dataclass
from RedisAssistant import RedisAssistant
from Region import Region

from ServerGroup import ServerGroup
from redis_utils import GAMEMODES_TO_BOOSTER_GROUPS, GAMEMODES_TO_GAME_DISPLAY, REDIS_KEYS_TO_GAME_DISPLAY, TEAM_SERVER_KEYS, npc_name_from_prefix


@dataclass
class GameOptions:
    prefix: str
    minPlayers: int = 8
    maxPlayers: int = 16
    arcadeGroup: bool = True 
    worldZip: str = 'arcade.zip'
    plugin: str = 'Arcade.jar'
    configPath: str = 'plugins/Arcade'
    pvp: bool = True 
    tournament: bool = False
    tournamentPoints: bool = False
    serverType: str = 'Minigames'
    addNoCheat: bool = True
    addWorldEdit: bool = False
    teamRejoin: bool = False
    teamAutoJoin: bool = True
    teamForceBalance: bool = False
    gameAutoStart: bool = True
    gameTimeout: bool = True
    gameVoting: bool = False
    mapVoting: bool = True
    rewardGems: bool = True
    rewardItems: bool = True
    rewardStats: bool = True
    rewardAchievements: bool = True
    hotbarInventory: bool = True
    hotbarHubClock: bool = True
    playerKickIdle: bool = True

    def _convert_to_server_group(self) -> ServerGroup:
        """Converts GameOptions to ServerGroup."""
        # need to check if servergroup already exists, and extract params if it does.
        ra = RedisAssistant.create_session()
        if ra.server_group_exists(self.prefix):
            return ServerGroup.convert_to_server_group(self.prefix)
        ra.redis.close()
        npcName = npc_name_from_prefix(self.prefix)
        boosterGroup = GAMEMODES_TO_BOOSTER_GROUPS.get(npcName, '')
        games = REDIS_KEYS_TO_GAME_DISPLAY.get(self.prefix, GAMEMODES_TO_GAME_DISPLAY.get(npcName, 'null'))
        if self.prefix == 'MIN':
            games = 'BaconBrawl,Lobbers,DeathTag,DragonEscape,Dragons,Evolution,Micro,MilkCow,Paintball,Quiver,Runner,Sheep,Snake,SneakyAssassins,Spleef,SquidShooter,TurfWars,WitherAssault'
        if self.prefix in TEAM_SERVER_KEYS.values():
            npcName = ''
        teamServerKey = TEAM_SERVER_KEYS.get(self.prefix, '')
        return ServerGroup(self.prefix, 512, 0, 0, 
                           ra.next_available_port(), self.arcadeGroup, 
                           self.worldZip, self.plugin, self.configPath, self.prefix, '', self.minPlayers,
                           self.maxPlayers, self.pvp, self.tournament, self.tournamentPoints, games, '', 
                           boosterGroup, self.serverType, self.addNoCheat, self.addWorldEdit, self.teamRejoin, 
                           self.teamAutoJoin, self.teamForceBalance, self.gameAutoStart, self.gameTimeout,
                           self.gameVoting, self.mapVoting, self.rewardGems, self.rewardItems, self.rewardStats, 
                           self.rewardAchievements, self.hotbarInventory, self.hotbarHubClock, self.playerKickIdle, 
                           teamServerKey=teamServerKey, npcName=npcName
                           )

    def create(self) -> None:
        """
        Creates ServerGroup key in Redis from GameOptions.
        Only creates key if not exists. 
        Does not rewrite data.

        >>> from GameType import GameType
        >>> from ServerType import ServerType
        

        >>> ServerType(GameType.Micro).create()
        None

        >>> ServerType('Micro').create()
        None
        
        """
        sg = self._convert_to_server_group()
        sg._create()

    def delete(self) -> None:
        """
        Deletes ServerGroup key in Redis.
        Only deletes key if exists (no need for checking manually).
        
        >>> from GameType import GameType
        >>> from ServerType import ServerType
       

        >>> ServerType(GameType.Micro).delete()
        None

        >>> ServerType('Micro').delete()
        None
        
        """
        sg = self._convert_to_server_group()
        sg._delete()

    def exists(self) -> bool:
        """Returns if ServerGroup with same prefix exists."""
        ra = RedisAssistant.create_session()
        exists = ra.server_group_exists(self.prefix)
        ra.redis.close()
        return exists
