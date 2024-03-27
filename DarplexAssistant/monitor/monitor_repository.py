from typing import Iterator, Self

import toml
from repository import RedisRepository 
from server import MinecraftServer, ServerGroup
from utils.redis_utils import DEFAULT_TOML_CONF


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
        return iter(map(ServerGroup.convert_to_server_group, self.repository.get_server_groups()))

    def get_minecraft_servers(self) -> Iterator[MinecraftServer]:
        """
        Returns Iterator of MinecraftServer objects.
        Each MinecraftServer object represents a ServerStatus cache.
        """
        servers = (server.replace('serverstatus.minecraft.US.', '') 
                   for server in self.repository.get_available_minecraft_servers())
        return iter(map(MinecraftServer.convert_to_minecraft_server, servers))

    def get_alive_servers(self) -> Iterator[MinecraftServer]:
        """
        Returns Iterator of all alive MinecraftServers.
        MinecraftServer represents a ServerStatus cache in Redis.
        """
        return iter(filter(lambda server: server.exists and server.is_online,
                           self.get_minecraft_servers()))

    def get_dead_servers(self) -> Iterator[MinecraftServer]:
        """
        Returns Iterator of all dead MinecraftServers.
        MinecraftServer represents a ServerStatus cache in Redis.
        """
        return iter(filter(lambda server: server.exists and not server.is_online,
                           self.get_minecraft_servers()))

    def get_ram_in_use(self) -> int:
        """
        Returns total ram in use for all online `MinecraftServer`.
        """
        return sum(server.ram for server in self.get_alive_servers())

    def get_if_enough_ram_allocated(self, server_group: ServerGroup) -> bool:
        """
        Returns if enough ram is allocated for a `MinecraftServer` of type `ServerGroup` to be deployed. 
        (`MinecraftServer` has a relationship to `ServerGroup`)
        """
        with open('../config/config.toml', 'r') as fp:
            max_ram: int = toml.load(fp) \
                          .get('server_monitor_options', DEFAULT_TOML_CONF['server_monitor_options']) \
                          .get('ram')
        return server_group.ram + self.get_ram_in_use() <= max_ram

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

