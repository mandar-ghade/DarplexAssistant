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
    elif servers == GameType.ALL:
        it = iter(servers.value) # makes tuple of enums into iterator
    else:
        it = iter(servers)
    for server in it:
        yield ServerType(server)


def print_servers() -> None:
    """Returns all servers and their online statuses."""
    
    pass


def view_server_statuses() -> None:
    """Returns all servers' uptime information."""
    RedisAssistant.create_session().get_server_group_uptime()
    pass


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
        command()
        input('')

if __name__ == "__main__":
    main()
