import json
import os
import sys
from typing import Callable, Iterable, Iterator, Optional, Set
from GameType import GameType
from MinecraftServer import MinecraftServer
from RedisAssistant import RedisAssistant
from ServerGroup import ServerGroup
from ServerType import ServerType

LOGO = """

                                            ██████╗ ██╗     ███████╗██╗  ██╗     █████╗ ███████╗███████╗██╗███████╗████████╗ █████╗ ███╗   ██╗████████╗
                                            ██╔══██╗██║     ██╔════╝╚██╗██╔╝    ██╔══██╗██╔════╝██╔════╝██║██╔════╝╚══██╔══╝██╔══██╗████╗  ██║╚══██╔══╝
                                            ██████╔╝██║     █████╗   ╚███╔╝     ███████║███████╗███████╗██║███████╗   ██║   ███████║██╔██╗ ██║   ██║   
                                            ██╔═══╝ ██║     ██╔══╝   ██╔██╗     ██╔══██║╚════██║╚════██║██║╚════██║   ██║   ██╔══██║██║╚██╗██║   ██║   
                                            ██║     ███████╗███████╗██╔╝ ██╗    ██║  ██║███████║███████║██║███████║   ██║   ██║  ██║██║ ╚████║   ██║   
                                            ╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   
                                                                                                                                                       

"""

def clear_screen() -> None:
    if os.name == 'posix':
        os.system('clear')
    else:
        os.system('cls')


def menu() -> None:
    print(LOGO)
    print(70 * ' ' + 'Welcome to Redis Assistant!\n\n')
    print(79 * ' ' + 'Commands\n\n')
    print(52 * ' ' + 'printservers : Returns all servers and their online statuses.\n')
    print(52 * ' ' + 'server-status-info : Returns all servers uptime information.\n')
    print(52 * ' ' + 'redis-info : View all current redis keys.')
    print(52 * ' ' + 'setup-redis : Sets up multiple game redis keys. Sends you into setup mode.')
    print(52 * ' ' + 'create-server-group : Create particular game server. Enters you into setup mode.')
    print(52 * ' ' + 'edit-server-group : Edit existing redis key options. Enters you into setup mode.')
    print(52 * ' ' + 'view-server-group-info : View existing redis key options. Enters you into viewer mode.') 
    print(52 * ' ' + 'deploy-servergroup : Deploy server group. Starts up server.\n')
    print(52 * ' ' + 'start-monitor : Start ServerMonitor.')
    print(52 * ' ' + 'monitor : Links you to DarplexMonitor.')
    print(52 * ' ' + 'exit : Exits the program.')


def print_servers() -> None:
    """Returns all servers and their online statuses."""
    
    pass


def return_minecraft_server_if_online(server: MinecraftServer) -> Optional[MinecraftServer]:
    if server.is_online:
        return server


def view_server_statuses() -> None:
    """
    Returns all servers' uptime information.
    """
    ra = RedisAssistant.create_session()
    server_group_names = ra.get_server_groups()
    for server_group_name in server_group_names:
        prefix = server_group_name.strip('servergroup.')
        server_group: ServerGroup = ServerGroup.convert_to_server_group(prefix)
        servers = set(list(server_group.servers).copy())
        online_servers: Set[MinecraftServer] = set(filter(return_minecraft_server_if_online, servers))
        offline_servers: Set[MinecraftServer] = servers.difference(online_servers)
        print(f'- {prefix}:')
        print(f'    - Port Section: {server_group.portSection}')
        print(f'    - Ram: {server_group.ram}MB')
        print(f'    - Total Servers: {server_group.totalServers}')
        print(f'    - Joinable Servers: {server_group.joinableServers}')
        print(f'    - Offline Servers: {len(offline_servers)}')
        print(f'    - Online Servers: {len(online_servers)}')
        if len(online_servers) + len(offline_servers) > 0:
            print(f'    - Servers:')
        for online_server in online_servers:
            print(f'        - {online_server.name} (Online):')
            print(f'            - Port: {online_server.port}')
            print(f'            - Uptime: Up since {online_server.start_up_date}') # convert to Datetime later
            print(f'            - RAM: {online_server.ram}MB') 
            print(f"            - Players: {online_server.player_count}")
            if online_server.game is not None:
                print(f'            - Arcade Stats:')
                print(f'                - Game: {online_server.game}')
                print(f'                - Mode: {online_server.mode}')
                print(f'                - Status: {online_server.status.value}') # value will never return None
                print(f'                - Joinable: {online_server.joinable.value}') # value will never return None
        for offline_server in offline_servers:
            print(f'        - {offline_server.name} (Offline):')
            print(f'            - Port: {offline_server.port}')
            print(f'            - Offline since: {offline_server.current_time}') # convert to Datetime later
            print(f'            - RAM: {offline_server.ram}MB') 
            print(f'            - Players: {offline_server.player_count}')
        print()


def get_redis_info() -> None:
    """View all current redis keys."""
    pass


def setup_redis() -> None:
    """
    Interactive menu & gui.
    Sets up multiple game redis keys. Sends user into setup mode."""
    pass


def create_server_group() -> None:
    """
    Create particular Server Group. 
    Enters user into setup mode."""
    pass


def edit_server_group() -> None:
    """
    Edit existing redis key options.
    Enters user into setup mode.
    """
    pass


def view_server_group_info() -> None:
    """
    View existing redis key options. 
    Enters you into viewer mode.
    """
    pass


def deploy_server_group() -> None:
    """
    Deploy server group.
    Starts up server.
    """
    pass


def start_monitor() -> None: #async / different window?. Monitor logs
    """Start ServerMonitor."""
    print('listening.......')
    pass


def link_to_monitor() -> None:
    """Links you to DarplexMonitor."""
    pass


COMMAND_TO_FUNC: dict[str, Callable] = {
    'printservers': print_servers,
    'server-status-info': view_server_statuses,
    'redis-info': get_redis_info,
    'setup-redis': setup_redis,
    'create-server-group': create_server_group, # prints menu
    'edit-server-group': edit_server_group,
    'view-server-group-info': view_server_group_info,
    'deploy-servergroup': deploy_server_group,
    'start-monitor': start_monitor,
    'monitor': link_to_monitor,
    'exit': exit
}


def main() -> None:
    menu()
    while True:
        clear_screen()
        menu()
        command = input('>> ')
        command = COMMAND_TO_FUNC.get(command, None)
        if command is None:
            input('Command does not exist. Please try again.')
            continue
        clear_screen()
        command()
        input('')

if __name__ == "__main__":
    main()
