from pprint import pprint
from time import sleep
from typing import Iterator
from DarplexAssistant import RedisRepository
from DarplexAssistant.game.game_options import GameOptions
from DarplexAssistant.monitor.monitor_repository import get_monitor_repo
from DarplexAssistant.repository.redis_repository import get_redis_repo
from DarplexAssistant.server.default_server import DefaultServer
from DarplexAssistant.server.minecraft_server import Cache, MinecraftServer
from DarplexAssistant.server.server_group import ServerGroup
from DarplexAssistant.utils.region import Region


# print(ServerGroup.convert_to_server_group('Lobby').get_create_cmd(1))
with get_monitor_repo() as monitor_repo:
    print(set(monitor_repo.get_dead_servers()))


#with get_redis_repo() as repo:
#    with get_monitor_repo() as monitor_repo:
#        for server in monitor_repo.get_all_server_groups():
#            if server.prefix in ('Lobby', 'Clans', 'ClansHub', 'Staff'):
#                continue
#            if monitor_repo.get_if_enough_ram_allocated(server):
#                server.increment_total_servers()
#                print(f'INCREMENTED TOTAL SERVERS: {server.name}')
#            else:
#                print(f'NOT ENOUGH RAM: {server.name}')
#                continue
#            while len(list(monitor_repo.get_minecraft_server_by_group(server.name, server.region))) == 0:
#                sleep(5)

