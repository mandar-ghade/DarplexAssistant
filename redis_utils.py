from typing import Optional


ARCADE_DICT = {
    'name': '',
    'prefix': '',
    'ram': 512,
    'cpu': 1,
    'totalServers': 0,
    'joinableServers': 0,
    'portSection': '',
    'arcadeGroup': 'true',
    'minPlayers': '6',
    'maxPlayers': '20',
    'pvp': 'true',
    'tournament': 'false',
    'tournamentPoints': 'false',
    'serverType': 'Minigames',
    'teamRejoin': 'false',
    'teamAutoJoin':	'true',
    'teamForceBalance':	'false',
    'gameAutoStart': 'true',
    'gameTimeout': 'true',
    'rewardGems': 'true',
    'rewardItems': 'true',
    'rewardStats': 'true',
    'rewardAchievements': 'true',
    'hotbarInventory': 'true',
    'hotbarHubClock': 'true',
    'playerKickIdle': 'true',
    'games': '',
    'addNoCheat':	'true',
    'addWorldEdit':	'false',
    'worldZip':	'arcade.zip',
    'configPath':	'plugins/Arcade',
    'plugin':	'Arcade.jar',
    'npcName': '',
}

GAMEMODE_SERVERS = {
    "Master Builders": ("BLD", ),
    "Draw My Thing": ("DMT", ),
    "Micro Battles": ("MB", ),
    "Mixed Arcade": ("MIN", ),
    "Turf Wars": ("TF", ),
    "Speed Builders": ("SB", ),
    "Block Hunt": ("BH", ),
    "Cake Wars": ("CW2", "CW4"),
    "Survival Games": ("HG", "SG2"),
    "Skywars": ("SKY", "SKY2"),
    "The Bridges": ("BR", ),
    "Mine-Strike": ("MS", ),
    "Super Smash Mobs": ("SSM", "SSM2"),
    "Champions": ("DOM", "CTF"),
    "Clans": ("ClansHub", "Clans")
    # "Retro": ("RETRO", ),
    # "Nano Games": ("NANO", )
}

TEAM_SERVER_KEYS = {
    'SKY': 'SKY2',
    'HG': 'SG2',
    'SSM': 'SSM2',
    'DOM': 'CTF',
    'CW4': 'CW2',
}


REDIS_KEYS_TO_GAME_DISPLAY = {
    'CW2': 'CakeWarsDuos',
    'CW4': 'CakeWars4',
    'HG': 'SurvivalGames',
    'SG2': 'SurvivalGamesTeams',
    'SKY': 'Skywars',
    'SKY2': 'SkywarsTeams',
    'SSM': 'Smash',
    'SSM2': 'SmashTeams',
    'DOM': 'ChampionsDominate',
    'CTF': 'ChampionsCTF',
}

GAMEMODES_TO_GAME_DISPLAY = {
    'Master Builders': 'Build',
    'Draw My Thing': 'Draw',
    'Micro Battles': 'Micro',
    'Turf Wars': 'TurfWars', 
    'Speed Builders': 'SpeedBuilders', 
    'Block Hunt': 'HideSeek',
    'The Bridges': 'Bridges', 
    'Mine-Strike': 'MineStrike',
    # 'Nano Games': 'NanoGames'
}


GAMEMODES_TO_BOOSTER_GROUPS = {
    'Master Builders': 'MasterBuilders', 
    'Draw My Thing': 'Draw_My_Thing', 
    'Micro Battles': 'Arcade', 
    'Mixed Arcade': 'Arcade', 
    'Turf Wars': 'Arcade', 
    'Speed Builders': 'Speed_Builders', 
    'Block Hunt': 'Block_Hunt', 
    'Cake Wars': 'Cake_Wars', 
    'Survival Games': 'Survival_Games', 
    'Skywars': 'Skywars', 
    'The Bridges': 'Bridges', 
    'Mine-Strike': 'MineStrike', 
    'Super Smash Mobs': 'Smash_Mobs', 
    'Champions': 'Champions', 
    # 'Nano Games': 'Nano_Games'
}


def npc_name_from_prefix(prefix: str) -> str:
    try:
        return next(gamemode 
                    for gamemode, prefixes in GAMEMODE_SERVERS.items()
                    if prefix in prefixes)
    except StopIteration:
        return ''
