
import os
from pathlib import Path
import shutil
import toml

from DarplexAssistant.utils.redis_utils import DEFAULT_TOML_CONF, create_config_if_not_exists

def stop_server(server_name: str) -> None:
    create_config_if_not_exists()

    with open('../config/config.toml', 'r') as fp:
        servers_directory = toml.load(fp) \
                                .get('server_monitor_options', DEFAULT_TOML_CONF['server_monitor_options']) \
                                .get('servers_directory', Path.home() / 'mineplex' / 'servers')

    server_path = Path(servers_directory) / server_name

    os.system(f'screen -S {server_name}'
              f'-X kill && screen -S {server_name} -X quit')
    if server_path.exists(): 
        shutil.rmtree(server_path)

