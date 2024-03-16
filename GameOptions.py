
from dataclasses import dataclass


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
