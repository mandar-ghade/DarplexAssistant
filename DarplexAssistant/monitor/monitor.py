from pathlib import Path
from time import perf_counter, sleep
from typing import Callable
import toml

from DarplexAssistant.utils.redis_utils import CONFIG_PATH
from ..utils import create_config_if_not_exists, DEFAULT_TOML_CONF
from ..server import MinecraftServer


create_config_if_not_exists()

with open(CONFIG_PATH, 'r') as fp:
    data = toml.load(fp).get('server_monitor_options', DEFAULT_TOML_CONF['server_monitor_options'])


MAX_RAM: int = data.get('ram', 512)
DEFAULT_BASE_DIR = Path.home() / 'mineplex'
SERVER_DIR = Path(data.get('servers_directory'))
JARS_DIRECTORY = Path(data.get('jars_directory'))
WORLD_ZIP_DIR = Path(data.get('world_zip_folder_directory'))

processes: list[Callable[[Callable, int], None]] = []


def start_or_restart_server(server: MinecraftServer, 
                            reason = '') -> None:
    cmd = server.get_create_cmd()
    if server.is_online and not server._needs_restart() and reason != 'Restart': # returns
        return # does not need to happen


def check_servers_needing_restart() -> None:
    """
    Checks when ServerGroup undergoes Restart or shuts down for any apparent reason. 
    """


def check_server_count_change() -> None:
    """
    Checks if `totalServers` or `joinableServers` changes for a ServerGroup
    Using timer
    """

def check_personal_or_mcs() -> None:
    """
    Checks if Personal, Community, or Event servers need to be deployed
    """
    # TODO: Scan `COM`, `EVENT`, *, serverType == 'Player' 



def start() -> None:
    # TODO: Concurrency module
    pass


def stop() -> None:
    for process in processes:
        ...

