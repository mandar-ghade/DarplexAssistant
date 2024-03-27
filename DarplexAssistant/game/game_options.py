from dataclasses import dataclass
from typing import ClassVar, Self, Union

from ..repository import RedisRepository 
from ..server import ServerGroup
from ..utils import GAMEMODES_TO_BOOSTER_GROUPS, GAMEMODES_TO_GAME_DISPLAY, REDIS_KEYS_TO_GAME_DISPLAY, TEAM_SERVER_KEYS, npc_name_from_prefix

type Game = tuple[bool | int | str, ...]

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
    
    Micro: ClassVar[Game] = ('MB',)
    MixedArcade: ClassVar[Game] = ('MIN', 8, 24)
    Draw: ClassVar[Game] = ('DMT', 5, 8)
    Build: ClassVar[Game] = ('BLD', 8, 12)
    TurfWars: ClassVar[Game] = ('TF', 8, 16)
    SpeedBuilders: ClassVar[Game] = ('SB', 4, 8)
    HideSeek: ClassVar[Game] = ('BH', 12, 24)
    CakeWarsDuos: ClassVar[Game] = ('CW2', 10, 16)
    CakeWarsTeams: ClassVar[Game] = ('CW4', 10, 16)
    SurvivalGames: ClassVar[Game] = ('HG', 12, 24)
    SurvivalGamesTeams: ClassVar[Game] = ('SG2', 12, 24)
    Skywars: ClassVar[Game] = ('SKY', 8, 12)
    SkywarsTeams: ClassVar[Game] = ('SKY2', 8, 12)
    Bridges: ClassVar[Game] = ('BR', 20, 40)
    MineStrike: ClassVar[Game] = ('MS', 8, 16)
    Smash: ClassVar[Game] = ('SSM', 4, 6)
    SmashTeams: ClassVar[Game] = ('SSM2', 4, 6)
    ChampionsDOM: ClassVar[Game] = ('DOM', 8, 10)
    ChampionsCTF: ClassVar[Game] = ('CTF', 10, 16)
    Clans: ClassVar[Game] = ('Clans', 1, 50, False, 
                        'clans.zip', 'Clans.jar', 
                        'plugins/Clans', False, False, 
                        False, 'dedicated', False, 
                        True, False, False, 
                        False, False, True, 
                        False, False, True, 
                        True, True, True, 
                        False, True, False)
    ClansHub: ClassVar[Game] = ('ClansHub', 1, 50, False, 
                        'clanshub.zip', 'ClansHub.jar', 
                        'plugins/ClansHub', False, False, 
                        False, 'dedicated', False, 
                        True, False, False, 
                        False, False, True, 
                        False, False, True, 
                        True, True, True, 
                        False, True, False)

    def _convert_to_server_group(self) -> ServerGroup:
        """Converts GameOptions to ServerGroup."""
        ra = RedisRepository.create_session()
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
        ra = RedisRepository.create_session()
        exists = ra.server_group_exists(self.prefix)
        ra.redis.close()
        return exists

    @classmethod
    def convert_from_game(cls, 
        game_options: tuple[Union[bool, int, str], ...]
    ) -> Self:
        """
        Expands tuple of GameOption arguments (class variable) into GameOptions object.
        Ex: 

        >>> from DarplexAssistant import GameOptions
        >>> GameOptions.convert_from_game_type(GameOptions.Micro)

        """
        return cls(*game_options) 

