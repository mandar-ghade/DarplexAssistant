from .server_group import ServerGroup

class DefaultServer:
    Lobby: ServerGroup = ServerGroup('Lobby', 512, 0, 0, None,
                                     False, 'lobby.zip', 'Hub.jar', 'plugins/Hub/', 'Lobby')
    Staff: ServerGroup = ServerGroup('Staff', 512, 0, 0, None,
                                     False, 'arcade.zip', 'StaffServer.jar', 'plugins/StaffServer/', 
                                     'Staff', serverType='Minigames', staffOnly=True)

