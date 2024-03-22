from dataclasses import dataclass
from GameOptions import GameOptions
from GameType import GameType

GAME_TYPE_TO_GAME_OPTIONS: dict[GameType, GameOptions] = {
    GameType.Micro: GameOptions('MB'),
    GameType.MixedArcade: GameOptions('MIN', 8, 24),
    GameType.Draw: GameOptions('DMT', 5, 8),
    GameType.Build: GameOptions('BLD', 8, 12),
    GameType.TurfWars: GameOptions('TF', 8, 16),
    GameType.SpeedBuilders: GameOptions('SB', 4, 8),
    GameType.HideSeek: GameOptions('BH', 12, 24),
    GameType.CakeWarsDuos: GameOptions('CW2', 10, 16),
    GameType.CakeWarsTeams: GameOptions('CW4', 10, 16),
    GameType.SurvivalGames: GameOptions('HG', 12, 24),
    GameType.SurvivalGamesTeams: GameOptions('SG2', 12, 24),
    GameType.Skywars: GameOptions('SKY', 8, 12),
    GameType.SkywarsTeams: GameOptions('SKY2', 8, 12),
    GameType.Bridges: GameOptions('BR', 20, 40),
    GameType.MineStrike: GameOptions('MS', 8, 16),
    GameType.Smash: GameOptions('SSM', 4, 6),
    GameType.SmashTeams: GameOptions('SSM2', 4, 6),
    GameType.ChampionsDOM: GameOptions('DOM', 8, 10),
    GameType.ChampionsCTF: GameOptions('CTF', 10, 16),
    GameType.Clans: GameOptions('Clans', 1, 50, False, 
                        'clans.zip', 'Clans.jar', 
                        'plugins/Clans', False, False, 
                        False, 'dedicated', False, 
                        True, False, False, 
                        False, False, True, 
                        False, False, True, 
                        True, True, True, 
                        False, True, False),
    GameType.ClansHub: GameOptions('ClansHub', 1, 50, False, 
                        'clanshub.zip', 'ClansHub.jar', 
                        'plugins/ClansHub', False, False, 
                        False, 'dedicated', False, 
                        True, False, False, 
                        False, False, True, 
                        False, False, True, 
                        True, True, True, 
                        False, True, False)
}

class ServerTypeNotExistsException(Exception):
    """Raised when ServerType does not exist"""


@dataclass
class ServerType:
    server: GameType | str

    def __post_init__(self) -> None:
        assert (isinstance(self.server, str) or isinstance(self.server, GameType))
        if (isinstance(self.server, str) and self.server not \
                in tuple(map(lambda x: x.value, GAME_TYPE_TO_GAME_OPTIONS)))\
            or (isinstance(self.server, GameType) and self.server not in GAME_TYPE_TO_GAME_OPTIONS):
            raise ServerTypeNotExistsException
        if isinstance(self.server, str):
            self.options = next(iter(options for game_type, options in GAME_TYPE_TO_GAME_OPTIONS.items() 
                                      if game_type.value == self.server))
        elif isinstance(self.server, GameType):
            self.options: GameOptions = GAME_TYPE_TO_GAME_OPTIONS.get(self.server, GameOptions('MIN', 8, 24)) # default is MixedArcade for typing sake

    def create(self) -> None:
        """
        Create ServerGroup from ServerType.

        Usage:

        >>> ServerType('ChampionsDOM').create()
        None

        >>> ServerType(GameType.ChampionsDOM).create()
        None

        """
        self.options.create()

    def delete(self) -> None:
        self.options.delete()

    def exists(self) -> bool:
        return self.options.exists()

