
from dataclasses import dataclass
from RedisAssistant import RedisAssistant

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


    def convert_to_server_group(self, **kwargs) -> ServerGroup:
        npcName = npc_name_from_prefix(self.prefix)
        boosterGroup = GAMEMODES_TO_BOOSTER_GROUPS.get(npcName, '')
        games = REDIS_KEYS_TO_GAME_DISPLAY.get(self.prefix, GAMEMODES_TO_GAME_DISPLAY.get(npcName, 'null'))
        if self.prefix == 'MIN':
            games = 'BaconBrawl,Lobbers,DeathTag,DragonEscape,Dragons,Evolution,Micro,MilkCow,Paintball,Quiver,Runner,Sheep,Snake,SneakyAssassins,Spleef,SquidShooter,TurfWars,WitherAssault'
        teamServerKey = TEAM_SERVER_KEYS.get(self.prefix, '')
        return ServerGroup(self.prefix, 512, 0, 0, 
                           RedisAssistant.create_session().next_available_port(), self.arcadeGroup, 
                           self.worldZip, self.plugin, self.configPath, self.prefix, '', self.minPlayers,
                           self.maxPlayers, self.pvp, self.tournament, self.tournamentPoints, games, '', 
                           boosterGroup, self.serverType, self.addNoCheat, self.addWorldEdit, self.teamRejoin, 
                           self.teamAutoJoin, self.teamForceBalance, self.gameAutoStart, self.gameTimeout,
                           self.gameVoting, self.mapVoting, self.rewardGems, self.rewardItems, self.rewardStats, 
                           self.rewardAchievements, self.hotbarInventory, self.hotbarHubClock, self.playerKickIdle, 
                           teamServerKey=teamServerKey, npcName=npcName
                           )


