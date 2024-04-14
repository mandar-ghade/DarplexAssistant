from pathlib import Path


SERVER_PROPERTIES: dict[str, str | bool] = {
    'server-port': '25565', # default
    'online-mode': False,
    'announce-player-achievements': False,
    'spawn-monsters': False,
    'allow-nether': False,
    'spawn-animals': False,
}


BUKKIT_YML_DICT: dict[str, str | bool] = {
    'settings': '',
    '  allow-end': False,
}

SPIGOT_YML_DICT: dict[str, str | bool] = {
    'settings': '',
    '  bungeecord': True,
}

MICROSERVICES = ('AMPLIFIERS', 'ANTISPAM', 'ENDERCHEST', 'BANNER')
REDIS_CONN_TYPES = ('MASTER', 'SLAVE')
REDIS_CONN_NAMES = ('DefaultConnection', 'ServerStatus')
DATABASES = ('ACCOUNT', 'QUEUE', 'MINEPLEX', 'MINEPLEX_STATS', 'PLAYER_STATS', 'MSSQL_MOCK')


def write_to_file(path: Path, data: dict[str, str | bool] | dict[str, str], symbol = ': ') -> None:
    with open(path, 'w') as writer:
        writer.write('\n'.join((name + symbol + (str(data[name]).lower() 
                                                 if isinstance(data[name], bool) 
                                                 else str(data[name])) 
                                for name in data)))

