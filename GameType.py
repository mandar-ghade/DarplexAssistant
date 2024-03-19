from enum import Enum

class GameType(Enum):
    Micro = 'Micro'
    MixedArcade = 'MixedArcade'
    Draw = 'Draw'
    Build = 'Build'
    TurfWars = 'TurfWars'
    SpeedBuilders = 'SpeedBuilders'
    HideSeek = 'HideSeek'
    CakeWarsDuos = 'CakeWarsDuos'
    CakeWarsTeams = 'CakeWarsTeams'
    SurvivalGames = 'SurvivalGames'
    SurvivalGamesTeams = 'SurvivalGamesTeams' 
    Skywars = 'Skywars'
    SkywarsTeams = 'SkywarsTeams'
    Bridges = 'Bridges'
    MineStrike = 'MineStrike'
    Smash = 'Smash'
    SmashTeams = 'SmashTeams'
    ChampionsDOM = 'ChampionsDOM'
    ChampionsCTF = 'ChampionsCTF'
    Clans = 'Clans'
    ClansHub = 'ClansHub'
    ALL = (Micro, MixedArcade, Draw, Build, 
           TurfWars, SpeedBuilders, HideSeek, CakeWarsDuos, 
           CakeWarsTeams, SurvivalGames, SurvivalGamesTeams,
           Skywars, SkywarsTeams, Bridges, MineStrike, Smash,
           SmashTeams, ChampionsDOM, ChampionsCTF, Clans, ClansHub)
