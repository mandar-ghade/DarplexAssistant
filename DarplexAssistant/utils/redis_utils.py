import os
from pathlib import Path
from typing import Optional

import toml
from .region import Region


CONFIG_PATH = (Path(__file__) / '../../' / 'config' / 'config.toml').resolve()


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


DEFAULT_TOML_CONF: dict[str, dict[str, str | int | list]] = {
    'redis_user': {
        'redis_address': '127.0.0.1',
        'redis_port': 6379
    },
    'server_monitor_options': {
        'region': 'US',
        'ram': 6000,
        'servers_directory': 'home/mineplex/servers',
        'jars_directory': 'home/mineplex/jars',
        'world_zip_folder_directory': 'home/mineplex/worlds',
        'traditional_db_config': False,
        'excluded_servers': [],
    },
    'sql': {
        'address': '127.0.0.1',
        'port': 3306,
        'username': 'root',
        'password': 'password'
    },
    'api': {
        'address': '127.0.0.1'
    },
    'microservice_ports': {
        'accounts': 1000,
        'amplifiers': 1000,
        'antispam': 1000,
        'enderchest': 1000,
        'banner': 1000
    }
}


def npc_name_from_prefix(prefix: str) -> str:
    for gamemode, prefixes in GAMEMODE_SERVERS.items():
        if prefix not in prefixes:
            continue
        return gamemode
    return ''


def get_region_by_str(region_str: str) -> Region:
    """
    Returns matching `Region` region_str.
    Defaults to Region.ALL.
    """
    for region in Region:
        if region.value != region_str:
            continue
        return region
    return Region.ALL #failsafe

def create_config_if_not_exists() -> None:
    if not os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'w') as fp:
            toml.dump(DEFAULT_TOML_CONF, fp)

