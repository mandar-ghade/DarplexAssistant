from DarplexAssistant.monitor.monitor_repository import get_monitor_repo
from DarplexAssistant.repository.redis_repository import get_redis_repo
from DarplexAssistant.server.server_group import ServerGroup
from DarplexAssistant.utils.region import Region

print(ServerGroup.convert_to_server_group('Lobby').get_create_cmd(1))

#with get_monitor_repo() as monitor_repo:
    #server_groups = monitor_repo.get_all_server_groups()
    #for sg in server_groups:
    #    print(sg.name, sg.region, set(sg.servers))
