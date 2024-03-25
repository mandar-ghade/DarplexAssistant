from datetime import datetime, timedelta
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
    print(52 * ' ' + 'server-status-info : Returns detailed server uptime statistics.\n')
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
    """
    Returns all servers and their online statuses.
    (Simplified version of view_server_statuses)
    """
    ra = RedisAssistant.create_session()
    server_group_names = set(ra.get_server_groups())
    if len(set(server_group_names)) > 0:
        largest_sg_name: str = next(iter(sorted(server_group_names, key=len, reverse=True)))
        largest_output_str_len = len(f'[{largest_sg_name}] |')
    for server_group_name in sorted(server_group_names):
        output_str = f'[{server_group_name}]'
        output_str += ' ' * (largest_output_str_len - len(output_str) - 1) + '| '
        init_output_len = len(output_str)
        prefix = server_group_name.replace('servergroups.', '')
        server_group = ServerGroup.convert_to_server_group(prefix)
        total_servers = set(server_group.servers)
        online_servers: set[MinecraftServer] = set(server for server in total_servers if server.is_online)
        player_count = sum(server.player_count for server in online_servers)
        status = 'Online' if len(online_servers) > 0 else 'Offline'
        output_str += f'Port Section: {server_group.portSection} | Servers {status} '
        if len(online_servers) > 0:
            output_str += f'| Players: {player_count} ' \
                          f'| {len(online_servers)}/{len(total_servers)} servers launched ' \
                           '|\n'
            output_str += f'\n'.join(f'{' ' * (init_output_len - 2)}' 
                                     f'| {online_serv.name} '
                                     f'| Port: {online_serv.port} '
                                     f'| Players: {online_serv.player_count}/{online_serv.max_player_count} '
                                      '|'
                                     for online_serv in online_servers)
        print(output_str)
    ra.redis.close()


def view_server_statuses() -> None:
    """
    Returns detailed server uptime statistics.
    """
    ra = RedisAssistant.create_session()
    server_group_names = ra.get_server_groups()
    max_ram = 0
    ram_usage = 0
    for server_group_name in server_group_names:
        prefix = server_group_name.replace('servergroups.', '')
        server_group: ServerGroup = ServerGroup.convert_to_server_group(prefix)
        servers = set(server_group.servers)
        online_servers = set(server for server in servers if server.is_online)
        offline_servers: Set[MinecraftServer] = servers.difference(online_servers)
        print(f'- {prefix}:')
        print(f'    - Port Section: {server_group.portSection}')
        print(f'    - Max Ram: {server_group.ram}MB')
        print(f'    - Total Servers: {server_group.totalServers}')
        print(f'    - Joinable Servers: {server_group.joinableServers}')
        if len(online_servers) + len(offline_servers) > 0:
            print(f'    - Servers Launched: {len(online_servers)}/{len(servers)}')
            print(f'    - Total Players: {sum(server.player_count for server in online_servers)}')
            print(f'    - Servers:')
        for online_server in online_servers:
            max_ram += server_group.ram
            ram = online_server.ram
            ram_usage += ram
            print(f'        - {online_server.name} (Online):')
            print(f'            - Port: {online_server.port}')
            print(f'            - Startup Date: {online_server.start_up_date}') # will never be none if online
            print(f'            - Uptime: {online_server.uptime} hours')
            print(f'            - RAM usage: {ram}MB/{server_group.ram}MB')
            print(f'            - Players: {online_server.player_count}/{server_group.maxPlayers}')
            if online_server.game is not None:
                print(f'            - Arcade Stats:')
                print(f'                - Game: {online_server.game}')
                print(f'                - Mode: {online_server.mode}')
                print(f'                - Status: {online_server.status.value}') # value will never return None
                print(f'                - Joinable: {online_server.joinable.value}') # value will never return None
        for offline_server in offline_servers:
            print(f'        - {offline_server.name} (Offline):')
            print(f'            - Port: {offline_server.port}')
            print(f'            - Offline since: {offline_server.current_time}') 
            print(f'            - Last uptime: {offline_server.uptime} hours') 
        print()
    if max_ram != 0: 
        print(f'Total ram usage: {ram_usage}MB/{max_ram}MB; {round((ram_usage / max_ram) * 100)}% ram usage.')
    ra.redis.close()


def get_redis_info() -> None:
    """View all current redis keys."""
    ra = RedisAssistant.create_session()
    keys = sorted(ra.redis.scan_iter('*'))
    for key in keys:
        print(key)


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

