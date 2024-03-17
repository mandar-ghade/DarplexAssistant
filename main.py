import os, sys

LOGO = """

                                            ██████╗ ██╗     ███████╗██╗  ██╗     █████╗ ███████╗███████╗██╗███████╗████████╗ █████╗ ███╗   ██╗████████╗
                                            ██╔══██╗██║     ██╔════╝╚██╗██╔╝    ██╔══██╗██╔════╝██╔════╝██║██╔════╝╚══██╔══╝██╔══██╗████╗  ██║╚══██╔══╝
                                            ██████╔╝██║     █████╗   ╚███╔╝     ███████║███████╗███████╗██║███████╗   ██║   ███████║██╔██╗ ██║   ██║   
                                            ██╔═══╝ ██║     ██╔══╝   ██╔██╗     ██╔══██║╚════██║╚════██║██║╚════██║   ██║   ██╔══██║██║╚██╗██║   ██║   
                                            ██║     ███████╗███████╗██╔╝ ██╗    ██║  ██║███████║███████║██║███████║   ██║   ██║  ██║██║ ╚████║   ██║   
                                            ╚═╝     ╚══════╝╚══════╝╚═╝  ╚═╝    ╚═╝  ╚═╝╚══════╝╚══════╝╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   
                                                                                                                                                       

"""

def menu() -> None:
    print(LOGO)
    print(70 * ' ' + 'Welcome to Darplex Assistant!\n\n')
    print(79 * ' ' + 'Commands\n\n')
    print(52 * ' ' + 'printservers : Returns all servers and their online statuses.')
    print(52 * ' ' + 'redis-info : View all current redis keys.') 
    print(52 * ' ' + 'setup-redis : Sets up multiple game redis keys. Sends you into setup mode.') 
    print(52 * ' ' + 'create-server : Create particular game server. Enters you into setup mode.') 
    print(52 * ' ' + 'edit-server : Edit existing redis key options. Enters you into setup mode.') 
    print(52 * ' ' + 'monitor : Links you to DarplexMonitor.') 
    print(52 * ' ' + 'exit : Exits the program.')


def main() -> None:
    menu()
    print('listening...')


if __name__ == "__main__":
    main()
