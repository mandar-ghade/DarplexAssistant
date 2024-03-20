import json
import os
import sys
from typing import Callable, Iterable, Iterator
from GameType import GameType
from RedisAssistant import RedisAssistant
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


def gametypes_iterator_to_options(servers: Iterable[GameType] | GameType) -> Iterator[ServerType]:
    if isinstance(servers, GameType) and servers != GameType.ALL:
        yield ServerType(servers)
        return
    elif isinstance(servers, GameType) and servers == GameType.ALL:
        it = iter(servers.value) # makes tuple of enums into iterator
    else:
        it = iter(servers)
    for server in it:
        yield ServerType(server)


def print_servers() -> None:
    """Returns all servers and their online statuses."""
    
    pass

# Could be simplified to just using a map function...
# More than one name per group? (DOM-2, DOM-1, ...) for DOM
def extract_group_name_from_servers(groups: Iterable[dict[str, str | int]]) -> Iterator[str]:
    """
    Returns group name from Iterator of server groups. 

    Use in coordination with `RedisAssistant`.

    Example usage:

    >>> from RedisAssistant import RedisAssistant
    >>> groups = RedisAssistant.create_session().get_server_group_uptime()
    >>> servers = (group for group, is_online in groups if is_online)
    >>> extract_group_name_from_servers(servers)
    """
    it = iter(groups)

    for group in groups:
        yield str(group.get('_group'))


def strip_servergroup_label(server_group: str) -> str:
    """Strips ServerGroup label. Returns ServerGroup name.
    >>> strip_servergroup_label('servergroups.MIN')
    'MIN'
    """
    return server_group.replace('servergroups.', '') 

#perhaps I should just integrate ServerStatus groups instead of using confusing dicts?
def view_server_statuses() -> None:
    """
    Returns all servers' uptime information.

    (Will rewrite using ServerStatus and ServerGroup classes to remove hard-to-read code)
    """
    ra = RedisAssistant.create_session()
    groups = ra.get_server_group_uptime()
    online_servers = (group for group, is_online in groups if is_online)
    online_servers_copy = list(online_servers).copy() # done because online_servers gets wiped of its contents for some reason?
    offline_server_statuses = (group for group, is_online in groups if not is_online) # will perhaps be used later?
    online_server_names = set(extract_group_name_from_servers(online_servers))
    offline_server_names = set(map(strip_servergroup_label, ra.get_server_groups())).difference(online_server_names)
    print('Online Servers: ')
    for online_serv in online_servers_copy:
        print(f'- {online_serv.get("_name")}:')
        print(f'    - Port: {online_serv.get("_port")}')
        print(f'    - Uptime: Up since {online_serv.get("_startUpDate")}ms') # convert to Datetime later
        print(f'    - RAM: {online_serv.get("_ram")}MB') 
        print(f"    - Players: {online_serv.get('_playerCount')}")
        if online_serv.get('_motd') != 'A Minecraft Server': # For arcade groups
            motd = json.loads(str(online_serv.get("_motd")))
            print(f'    - Arcade Stats:')
            print(f'        - Game: {motd.get("_game")}')
            print(f'        - Mode: {motd.get("_mode")}')
            print(f'        - Status: {motd.get("_status")}')
            print(f'        - Joinable: {motd.get("_joinable")}')
    print('\nOffline Servers:')
    for offline_serv in offline_server_names:
        group = ra.convert_dict_to_server_group_insertable(offline_serv) # rename func very unreadible
        print(f'- {offline_serv}:')
        print(f'    - Port Section: {group.get("portSection")}')
        print(f'    - Ram: {group.get("ram")}MB')
        print(f'    - Total Servers: {group.get("totalServers")}')
        print(f'    - Joinable Servers: {group.get("joinableServers")}')


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
