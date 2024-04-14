from contextlib import contextmanager
import toml
from typing import Iterator, Optional, Self

from DarplexAssistant.repository.redis_repository import get_redis_repo
from DarplexAssistant.utils.region import Region
from ..repository import RedisRepository 
from ..server import MinecraftServer, ServerGroup
from ..utils import CONFIG_PATH, DEFAULT_TOML_CONF


class MonitorRepository:
    def __init__(self, repository: RedisRepository) -> None:
        self.repository = repository

    def close(self) -> None:
        """Closes the MonitorRepository session."""
        self.repository.redis.close()

    def get_all_server_groups(self) -> Iterator[ServerGroup]:
        """
        Returns Iterator of all Redis ServerGroups mapped to `ServerGroup` objects.
        `ServerGroup` object represents type of Server.
            - Contains vital information about `ram`, `totalServers`
            - `MinecraftServer` objects linked to `ServerGroup` represent deployed servers.
        """
        yield from map(ServerGroup.convert_to_server_group,
                       self.repository.get_server_groups())

    def get_minecraft_servers_by_region(self, region: Region) -> Iterator[MinecraftServer]:
        """Returns MinecraftServers by matching region"""
        yield from filter(lambda server: server.region == region,
                          self.get_minecraft_servers())

    @staticmethod
    def get_region_by_server_status(server_status_key: str) -> Region:
        return next(iter((region
                          for region in Region
                          if region.value in server_status_key)), Region.US)

    def get_minecraft_servers(self) -> Iterator[MinecraftServer]:
        """
        Returns Iterator of `MinecraftServer`.
        Each `MinecraftServer` represents a ServerStatus cache.
        
        Transposes all ServerStatus redis caches into MinecraftServer objects.
        """
        servers = self.repository.get_available_minecraft_servers()
        available_minecraft_servers = self.repository.get_available_minecraft_servers()
        if len(set(available_minecraft_servers).copy()) == 0:
            yield from ()
            return
        servers, regions = zip(*((server, self.get_region_by_server_status(server)) 
                   for server in self.repository.get_available_minecraft_servers())) # numpy transpose?
        yield from map(MinecraftServer.convert_to_minecraft_server, servers, regions)

    def get_minecraft_server_by_group(self, group: str, region: Region) -> Iterator[MinecraftServer]:
        yield from filter(lambda minecraft_server: minecraft_server.group == group 
                       and minecraft_server.region == region, self.get_minecraft_servers())

    def get_alive_servers(self, region: Optional[Region] = None) -> Iterator[MinecraftServer]:
        """
        Returns Iterator of all online `MinecraftServer`s.
        `MinecraftServer` represents a ServerStatus cache in Redis.

        Optional: `region` filters `MinecraftServer` by `Region`.
        """
        yield from filter(lambda server: (server.exists and
                                          server.is_online and  
                                          (server.region == region if region in (Region.US, None) else True)),
                           self.get_minecraft_servers())

    def get_dead_servers(self) -> Iterator[MinecraftServer]:
        """
        Returns Iterator of all dead `MinecraftServer`.
        MinecraftServer represents a ServerStatus cache in Redis.
        """
        yield from filter(lambda server: server.exists and not server.is_online,
                           self.get_minecraft_servers())

    def get_ram_in_use(self) -> int:
        """
        Returns total ram in use for all online `MinecraftServer`.
        """
        return sum(server.ram for server in self.get_alive_servers())

    def get_if_enough_ram_allocated(self, server_group: ServerGroup) -> bool:
        """
        Returns if enough ram is allocated for a `MinecraftServer` of type `ServerGroup` to be deployed. 
        `MinecraftServer` is an instance or node created based on `ServerGroup`.
            - Represents deployed Server.
        (`MinecraftServer` has a relationship to `ServerGroup`)
        """
        with open(CONFIG_PATH, 'r') as fp:
            max_ram: int = toml.load(fp) \
                          .get('server_monitor_options', DEFAULT_TOML_CONF['server_monitor_options']) \
                          .get('ram')
        return server_group.ram + self.get_ram_in_use() <= max_ram

    
    def kill_dead_servers(self) -> Iterator[MinecraftServer]:
        """Kills dead servers"""
        for server in self.get_dead_servers():
            try:
                server.kill_server()
            except Exception:
                continue
            yield server

    @classmethod
    def create_session(cls) -> Self:
        """
        Creates a MonitorRepository session using default connection information.
       
        Defaults: 
        - Address: 127.0.0.1
        - Port: 6379

        Change these in `config.toml`

        """
        return cls(RedisRepository.create_session())

@contextmanager
def get_monitor_repo() -> Iterator[MonitorRepository]:
    """For quick session in `MonitorRepository`. 
    Creates and closes `RedisRepository` session.
    """
    with get_redis_repo() as redis_repository:
        yield MonitorRepository(redis_repository) # does not need finally since connection auto-closes

