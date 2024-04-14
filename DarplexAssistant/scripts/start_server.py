
import os
from pathlib import Path
import shutil
import toml
from zipfile import ZipFile


from ..utils import (BUKKIT_YML_DICT, 
                     DATABASES,
                     DEFAULT_TOML_CONF,
                     CONFIG_PATH,
                     create_config_if_not_exists,
                     MICROSERVICES,
                     REDIS_CONN_NAMES,
                     REDIS_CONN_TYPES,
                     SERVER_PROPERTIES,
                     SPIGOT_YML_DICT,
                     write_to_file)



def start_server(
    port: int,
    ram: int,
    zip_file: str,
    plugin_file: str,
    config_path: str,
    server_group: str,
    server_name: str,
    is_us: bool,
    add_anticheat: bool,
    add_worldedit: bool
) -> None:
    """Creates Minecraft server locally based on `config.toml` configuration.
    For this module to work, modify:
    - `server_monitor_options`:
        - `ram`: max ram you want to allocate. (will not exceed usage threshold)
        - `server_directory`: path to your servers folder. Where your servers will be generated.
        - `jars_directory`: Directory of all your jar files.
        - `world_zip_folder_directory`: Directory of all zipped world files.
            - Ensure the following exist in the directory:
                - `lobby.zip` - Lobby 
                - `Lobby_MPS.zip` - For Multiplayer Private Servers (MPSes)
                - `Lobby_MCS.zip` - For Community Servers.
                - `arcade.zip` - For all Arcade servers.
                - `ClansHub.zip` - For ClansHub server.
            All zip files must contain a `world` folder.
        - `traditional_db_config`: If `db-config.dat` generation should be traditional.
            - `false` for all `mineplex-crepe` and `mineplex-reborn` users.
            - `true` for all `mineplex-reborn` and `mineplex-original` users.
            - Traditional output:
                ```
                ACCOUNT 127.0.0.1:3306/account user password
                PLAYER_STATS 127.0.0.1:3306/player_stats user password
                ```
            - Non-traditional output (custom):
                ```
                    ACCOUNT 127.0.0.1:3306 user password
                    PLAYER_STATS 127.0.0.1:3306 user password
                ```
        - `excluded_servers`:
            - List of servers you want DarplexServerMonitor to ignore
    - `sql`
    """
    create_config_if_not_exists()

    with open(CONFIG_PATH, 'r') as fp:
        data = toml.load(fp)

    monitor_options = data.get('server_monitor_options', DEFAULT_TOML_CONF['server_monitor_options'])
    sql_options = data.get('sql', DEFAULT_TOML_CONF['sql'])
    api_options = data.get('api', DEFAULT_TOML_CONF['api'])
    microservice_ports = data.get('microservice_ports', DEFAULT_TOML_CONF['microservice_ports'])

    DEFAULT_WORK_DIR = Path.home() / 'mineplex'
    SERVER_PATH = Path(monitor_options.get('servers_directory', DEFAULT_WORK_DIR / 'servers')) / server_name
    WORLD_PATH = Path(monitor_options.get('world_zip_folder_directory', DEFAULT_WORK_DIR / 'worlds'))
    JAR_PATH = Path(monitor_options.get('jars_directory', DEFAULT_WORK_DIR / 'jars')) 
    PLUGINS_DIR = SERVER_PATH / 'plugins'

    SQL_ADDRESS = os.environ.get('MYSQL_ADDRESS', sql_options.get('address', '127.0.0.1'))
    SQL_USERNAME = sql_options.get('username', 'root')
    SQL_PASSWORD = sql_options.get('password', 'password')
    SQL_PORT: int = sql_options('port', 3306)

    REDIS_ADDRESS = os.environ.get('REDIS_ADDRESS', 
                                   sql_options.get('redis_user', DEFAULT_TOML_CONF['redis_user']).get('redis_address', '127.0.0.1')) 

    MONITOR_ADDRESS = os.environ.get('MONITOR_ADDRESS', api_options.get('address', '127.0.0.1'))

    ACCOUNTS_PORT: int = microservice_ports.get('accounts', 1000)
    AMPLIFIERS_PORT: int = microservice_ports.get('amplifiers', 1000)
    ANTISPAM_PORT: int = microservice_ports.get('antispam', 1000)
    ENDERCHEST_PORT: int = microservice_ports.get('enderchest', 1000)
    BANNER_PORT: int = microservice_ports.get('banner', 1000)

    MICROSERVICE_PORTS = (AMPLIFIERS_PORT, ANTISPAM_PORT, ENDERCHEST_PORT, BANNER_PORT)

    if SERVER_PATH.exists():
        shutil.rmtree(SERVER_PATH)

    os.makedirs(SERVER_PATH)

    server_properties = SERVER_PROPERTIES.copy()
    server_properties['server-port'] = f'{port}'
   
    plugin_config_dict: dict[str, str] = {
        'webServer': f'http://{MONITOR_ADDRESS}:{ACCOUNTS_PORT}/',
        'serverstatus': '',
        '  group': server_group,
        '  name': server_name,
        '  us': str(is_us).lower(),
        '  connectionurl': f'{SQL_ADDRESS}:{SQL_PORT}',
        '  username': SQL_USERNAME,
        '  password': SQL_PASSWORD,
    }

    if not is_us:
        with open(SERVER_PATH / 'eu.dat', 'w') as _: # creates eu.dat file if Region != US
           pass 


    write_to_file(SERVER_PATH / 'server.properties', server_properties, '=')
    write_to_file(SERVER_PATH / 'bukkit.yml', BUKKIT_YML_DICT)
    write_to_file(SERVER_PATH / 'spigot.yml', SPIGOT_YML_DICT)

    shutil.copy(JAR_PATH / 'spigot.jar', SERVER_PATH)

    PLUGINS_DIR.mkdir()

    shutil.copy(JAR_PATH / plugin_file, PLUGINS_DIR)

    if add_anticheat and (JAR_PATH / 'AntiCheat.jar').exists():
        shutil.copy(JAR_PATH / 'AntiCheat.jar', PLUGINS_DIR)

    if add_worldedit and (JAR_PATH / 'WorldEdit.jar').exists():
        shutil.copy(JAR_PATH / 'WorldEdit.jar', PLUGINS_DIR)

    if (JAR_PATH / 'ViaVersion.jar').exists():
        shutil.copy(JAR_PATH / 'ViaVersion.jar', PLUGINS_DIR)
    

    with ZipFile(WORLD_PATH / zip_file, 'r') as zip_ref:
       zip_ref.extractall(SERVER_PATH)

    os.makedirs(SERVER_PATH / config_path)

    write_to_file(SERVER_PATH / config_path / 'config.yml', plugin_config_dict)


    with open(SERVER_PATH / 'api-config.dat', 'w') as writer:
        writer.write('\n'.join(
            f'{service}:\n  ip: {MONITOR_ADDRESS}\n  port: {port}'
            for service, port in zip(MICROSERVICES, MICROSERVICE_PORTS)
            ))

    with open(SERVER_PATH / 'redis-config.dat', 'w') as writer:
        writer.write('\n'.join(
                    f'{REDIS_ADDRESS} 6379 {conn_type} {name}'
                    for conn_type in REDIS_CONN_TYPES
                    for name in REDIS_CONN_NAMES
                    )
                )

    with open(SERVER_PATH / 'database-config.dat', 'w') as writer:
        writer.write('\n'.join(
                    f'{database} {SQL_ADDRESS} {SQL_USERNAME} {SQL_PASSWORD}'
                    for database in DATABASES
                    )
                )
        
    os.system(f'cd \'{SERVER_PATH}\';'
              f'screen -XS {server_name} kill;' 
              f'screen -XS {server_name} quit;'
              f'screen -dmS {server_name} java -Xmx{ram}M -Xms{ram}M -jar spigot.jar')

