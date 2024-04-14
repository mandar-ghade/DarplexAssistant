from dataclasses import dataclass
from typing import ClassVar, Self, Union
from DarplexAssistant.repository.redis_repository import get_redis_repo

from DarplexAssistant.utils.redis_utils import GAMEMODE_SERVERS
from DarplexAssistant.utils.region import Region

from ..repository import RedisRepository 
from ..server import ServerGroup
from ..utils import GAMEMODES_TO_BOOSTER_GROUPS, GAMEMODES_TO_GAME_DISPLAY, REDIS_KEYS_TO_GAME_DISPLAY, TEAM_SERVER_KEYS, npc_name_from_prefix

class GameTypeNotExistsException(Exception):
    pass

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
    DEFAULT_GAMES: ClassVar[set[str]] = {'BaconBrawl',
                                         'Bridge',
                                         'ChampionsCTF',
                                         'ChampionsDOM',
                                         'Lobbers',
                                         'DeathTag',
                                         'DragonEscape',
                                         'Dragons'
                                         'Evolution',
                                         'Micro',
                                         'MilkCow',
                                         'Paintball',
                                         'Quiver',
                                         'Runner',
                                         'Sheep',
                                         'Snake',
                                         'SneakyAssassins',
                                         'Spleef',
                                         'SquidShooter',
                                         'TurfWars',
                                         'WitherAssault'}.union(REDIS_KEYS_TO_GAME_DISPLAY.values()) \
                                                         .union(GAMEMODES_TO_GAME_DISPLAY.values())
    
    @staticmethod
    def _get_npc_name(prefix: str) -> str:
        """Gets `npcName` by prefix.
        Manually check if it is a team server key using: 
        >>> GameOptions._is_team_server(prefix='...')
        (returns bool)
        If it is a team server, `npcName` should manually be set to '' before inserting.
        """
        for gamemode, prefixes in GAMEMODE_SERVERS.items():
            if prefix not in prefixes:
                continue
            return gamemode
        return ''

    @staticmethod
    def _get_booster_group(npc_name: str) -> str:
        return GAMEMODES_TO_BOOSTER_GROUPS.get(npc_name, '')

    @staticmethod
    def _get_games(prefix: str, npc_name: str) -> str:
        if prefix == 'MIN':
            return ','.join(GameOptions.DEFAULT_GAMES)
        return REDIS_KEYS_TO_GAME_DISPLAY.get(prefix, GAMEMODES_TO_GAME_DISPLAY.get(npc_name, 'null'))

    @staticmethod
    def _get_team_server_key(prefix: str) -> str:
        """Returns matching team server key to non-team server.
        Returns '' if DNE."""
        return TEAM_SERVER_KEYS.get(prefix, '')

    @staticmethod
    def _is_team_server(prefix: str) -> bool:
        """Returns whether ServerGroup is a team server.
        If it is, `npcName`=''"""
        return prefix in TEAM_SERVER_KEYS.values()

    def _get_server_group_args(self) -> tuple[str | bool | int | Region, ...]:
        """Returns ServerGroup insertable arguments."""
        npc_name = self._get_npc_name(self.prefix)
        booster_group = self._get_booster_group(npc_name)
        games = self._get_games(self.prefix, npc_name)
        if self._is_team_server(self.prefix):
            npc_name = ''
        team_server_key = self._get_team_server_key(self.prefix)
        with get_redis_repo() as repo:
            port = repo.next_available_port()
        return (self.prefix, 512, 0, 0,
                port, self.arcadeGroup, self.worldZip,
                self.plugin, self.configPath, self.prefix,
                '', self.minPlayers, self.maxPlayers,
                self.pvp, self.tournament, self.tournamentPoints,
                games, '', booster_group, self.serverType, self.addNoCheat,
                self.addWorldEdit, self.teamRejoin, self.teamAutoJoin,
                self.teamForceBalance, self.gameAutoStart, self.gameTimeout,
                self.gameVoting, self.mapVoting, self.rewardGems,
                self.rewardItems, self.rewardStats, self.rewardAchievements,
                self.hotbarInventory, self.hotbarHubClock, self.playerKickIdle,
                False, False, False, '', Region.US, team_server_key, '',
                '', npc_name)


    def _convert_to_server_group(self) -> ServerGroup:
        """Converts GameOptions to ServerGroup."""
        with get_redis_repo() as repository:
            if repository.server_group_exists(self.prefix):
                return ServerGroup.convert_to_server_group(self.prefix)
        server_group_insertable_arguments = self._get_server_group_args()
        return ServerGroup(*server_group_insertable_arguments) # type: ignore

    def create(self) -> None:
        """Creates ServerGroup key in Redis from GameOptions.
        Only creates key if not exists. 
        Does not rewrite data.

        >>> from DarplexAssistant import GameOptions
        >>> GameOptions.convert_from_game(GameOptions.MixedArcade).create()
        None

        """
        server_group = self._convert_to_server_group()
        server_group.create()

    def delete(self) -> None:
        """
        Deletes ServerGroup key in Redis.
        Only deletes key if exists (no need for checking manually).
        
        >>> from DarplexAssistant import GameOptions
        >>> GameOptions.convert_from_game(GameOptions.Micro).delete()
        None 
        
        """
        server_group = self._convert_to_server_group()
        server_group.delete()

    def overwrite(self) -> None:
        """
        Overwrites ServerGroup key in Redis from GameOptions.
        Usage:

        >>> from DarplexAssistant import GameOptions
        >>> GameOptions.convert_from_game(GameOptions.SkywarsTeams).overwrite()
        None

        """
        server_group = self._convert_to_server_group()
        server_group.overwrite()

    def exists(self) -> bool:
        """Returns if ServerGroup with same prefix exists."""
        
        with get_redis_repo() as repo:
            return repo.server_group_exists(self.prefix)

    @staticmethod
    def get_stored_games() -> dict[str, Game]:
        return dict((attr, getattr(GameOptions, attr))
                    for attr in dir(GameOptions)
                    if not callable(getattr(GameOptions, attr))
                    and not (attr.startswith('__') or attr[0].islower())
                    and attr != 'DEFAULT_GAMES')
    
    @classmethod
    def convert_from_game(cls, 
        game: Game | str
    ) -> Self:
        """
        Expands tuple of GameOption arguments (class variable) into GameOptions object.
        Ex: 

        >>> from DarplexAssistant import GameOptions
        >>> GameOptions.convert_from_game_type(GameOptions.Micro)
        GameOptions(prefix='MB', ...) 
        >>> GameOptions.convert_from_game_type('Micro')
        GameOptions(prefix='MB', ...)
        """
        games: dict[str, Game] = GameOptions.get_stored_games()
        if isinstance(game, str):
            game = games.get(game.strip(), '')
        if game == '' or game not in games.values():
            raise GameTypeNotExistsException()
        return cls(*game) # type: ignore

