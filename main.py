from colorama import Fore, Back, Style
from datetime import datetime, timedelta
import json
import os
from pprint import pprint
import sys
from typing import Callable, Iterable, Iterator, Optional, Set
from DarplexAssistant.game.game_options import Game, GameOptions

from DarplexAssistant.repository.redis_repository import get_redis_repo
from DarplexAssistant.server.default_server import DefaultServer
from DarplexAssistant.server.minecraft_server import MinecraftServer
from DarplexAssistant.server.server_group import ServerGroup

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
    print(52 * ' ' + 'tutorial : Takes you into the tutorial.\n\n')
    print(52 * ' ' + 'printservers : Returns all servers and their online statuses.\n')
    print(52 * ' ' + 'server-status-info : Returns detailed server uptime statistics.\n')
    print(52 * ' ' + 'redis-info : View all current redis keys.')
    print(52 * ' ' + 'setup-redis : Sets up multiple game redis keys. Sends you into setup mode.')
    print(52 * ' ' + 'create-server-group : Create particular game server. Enters you into setup mode.')
    print(52 * ' ' + 'edit-server-group : Edit existing redis key options. Enters you into setup mode.')
    print(52 * ' ' + 'view-server-group-info : View existing redis key options. Enters you into viewer mode.') 
    print(52 * ' ' + 'deploy-servergroup : Deploy server group. Starts up server.\n')
    print(52 * ' ' + 'setup-config-file : Setup config.toml file for ServerMonitor to work.')
    print(52 * ' ' + 'view-monitor-logs : View ServerMonitor logs.')
    print(52 * ' ' + 'attach-server-monitor : Attach ServerMonitor to screen.')
    print(52 * ' ' + 'start-monitor : Start ServerMonitor.')
    print(52 * ' ' + 'stop-monitor : Start ServerMonitor.')
    print(52 * ' ' + 'monitor : Links you to DarplexMonitor.')
    print(52 * ' ' + 'exit : Exits the program.')


def print_servers() -> None:
    """
    Returns all servers and their online statuses.
    (Simplified version of view_server_statuses)
    """
    with get_redis_repo() as repo:
        server_group_names = set(repo.get_server_groups())
    if len(set(server_group_names)) > 0:
        largest_sg_name: str = next(iter(sorted(server_group_names, key=len, reverse=True)))
        largest_output_str_len = len(f'[{largest_sg_name}] |')
    else:
        print('No ServerGroups found.')
        return
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

def tutorial() -> None:
    """Gives tutorial of features included DarplexAssistant"""
    pass


def view_server_statuses() -> None: #TODO: Update every 2-3 seconds until user input received. 
    """
    Returns detailed server uptime statistics.
    """
    with get_redis_repo() as repo:
        server_group_names = list(repo.get_server_groups()).copy()
    max_ram = 0
    ram_usage = 0
    if len(set(server_group_names)) == 0:
        print('No ServerGroups found.')
        return
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
            print(f'            - Startup Date: {online_server.start_up_date}')
            print(f'            - Uptime: {online_server.uptime} hours')
            print(f'            - RAM usage: {ram}MB/{server_group.ram}MB')
            print(f'            - Players: {online_server.player_count}/{server_group.maxPlayers}')
            if online_server.game is not None:
                print(f'            - Arcade Stats:')
                print(f'                - Game: {online_server.game}')
                print(f'                - Mode: {online_server.mode}')
                print(f'                - Status: {online_server.status.value}') # type: ignore
                print(f'                - Joinable: {online_server.joinable.value}') # type: ignore
        for offline_server in offline_servers:
            print(f'        - {offline_server.name} (Offline):')
            print(f'            - Port: {offline_server.port}')
            print(f'            - Offline since: {offline_server.current_time}') 
            print(f'            - Last uptime: {offline_server.uptime} hours') 
        print()
    if max_ram != 0: 
        print(f'Total ram usage: {ram_usage}MB/{max_ram}MB; {round((ram_usage / max_ram) * 100)}% of ram allocated has been used.')


def get_redis_info() -> None:
    """View all current redis keys."""
    with get_redis_repo() as repo:
        for key in sorted(repo.redis.scan_iter('*')):
            print(key)


def print_setup_menu(groups: dict[int, ServerGroup], selected: set[str]) -> None:
    """Prints servers and whether they exist
    Used in `setup_redis`
    """
    for i, group in groups.items():
        output = ' '
        if group.prefix in selected:
            output = '*'
        output += f' {i}) servergroups.{group.prefix} | '
        if group._exists(): 
            output = Fore.GREEN + output + 'ONLINE'
        else:
            output = Fore.RED + output + 'OFFLINE'
        print(output)
    print(Fore.CYAN)
    print('\n')


def setup_redis() -> None:
    """
    Interactive menu & gui.
    Sets up multiple game redis keys. Sends user into setup mode.
    """
    games: dict[str, Game] = GameOptions.get_stored_games().copy()
    all_servers: list[ServerGroup] = [DefaultServer.Lobby,
                                      DefaultServer.Staff,
                                      *map(lambda game: GameOptions 
                                                        .convert_from_game(game)
                                                        ._convert_to_server_group(),
                                           games.keys())] # get servers which exist but aren't recognized
    servers: dict[int, ServerGroup] = dict((i+1, group) for i, group in enumerate(all_servers))
    selected = set[str]()
    while True:
        print(Fore.MAGENTA + 'Available ServerGroups: \n')
        print_setup_menu(servers, selected)
        sg_input = input('Which group(s) would you like to edit? (type exit to exit)> ')
        if sg_input == 'exit':
            break
        if not sg_input.isdigit() or int(sg_input) not in servers:
            input(Fore.RED + 'Invalid input. Please try again')
            clear_screen()
            continue
        sg_input = int(sg_input)
        selected.add(servers[sg_input].prefix)
        clear_screen()
    clear_screen()
    print(Fore.CYAN + 'Selected groups:')
    selected_servers: dict[int, ServerGroup] = dict(filter(lambda pair: pair[1].prefix in selected,
                                                           servers.items()))
    print_setup_menu(selected_servers, selected)
    input('Press any key to enter menu')
    clear_screen()
    options = ['CREATE', 'EDIT', 'DELETE'] 
    for i, (key, server) in enumerate(selected_servers.items()):
        print(Fore.BLUE + f'Selected ({i+1}/{len(selected_servers)}) =>')
        print_setup_menu({key: server}, {''})
        print(Fore.MAGENTA + 'Options:')
        print(Fore.LIGHTGREEN_EX + '\n'.join(f'- {n+1}) {option}' for n, option in enumerate(options)))
        print(Fore.CYAN)
        option = input('')
        clear_screen()
    print(Fore.WHITE)



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


def start_monitor() -> None: 
    """Starts ServerMonitor."""
    pass


def stop_monitor() -> None:
    pass


def link_to_monitor() -> None:
    """Links you to DarplexMonitor."""
    pass


def view_monitor_logs() -> None:
    """Clears screen and shows ServerMonitor logs."""
    pass


def attach_monitor():
    """Attaches ServerMonitor to screen"""
    pass


COMMAND_TO_FUNC: dict[str, Callable] = {
    'tutorial': tutorial,
    'printservers': print_servers,
    'server-status-info': view_server_statuses,
    'redis-info': get_redis_info,
    'setup-redis': setup_redis,
    'create-server-group': create_server_group, # prints menu
    'edit-server-group': edit_server_group,
    'view-server-group-info': view_server_group_info,
    'deploy-servergroup': deploy_server_group,
    'view-monitor-logs': view_monitor_logs,
    'attach-server-monitor': attach_monitor,
    'start-monitor': start_monitor,
    'stop-monitor': stop_monitor,
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

