from contextlib import contextmanager
import json
from random import randint
from redis import Redis
from typing import Any, ContextManager, Iterator, Optional, Self
import toml
from ..utils import CONFIG_PATH, create_config_if_not_exists, Region

    
class RedisRepository:
    def __init__(self, host: str, port: int) -> None:
        self.redis = Redis(host=host, port=port, db=0, decode_responses=True)
    
    def close_connection(self) -> None:
        """Closes redis connection."""
        self.redis.close()

    def server_group_exists(self, prefix: str) -> bool:
        """Returns whether a server-group exists based on prefix."""
        for _ in self.redis.scan_iter(f'servergroups.{prefix}'):
            return True
        return False

    def delete_server_group(self, prefix: str) -> None:
        """Deletes `ServerGroup` with specified server prefix from Redis.
        If `ServerGroup cache DNE, method does nothing.
        """
        if not self.server_group_exists(prefix):
            return
        self.redis.srem('servergroups', prefix)
        self.redis.delete(f'servergroups.{prefix}')

    def get_if_port_conflicts(self, port: int) -> bool:
        """Returns if `port` conflicts with any existing port sections in the Redis db."""
        return any(port - 10 <= port_section <= port + 10
                   for port_section in 
                   map(lambda group: int(self.redis.hget(group, 'portSection') or 0),
                                         self.get_server_groups()))

    def create_server_group(self, prefix: str, data: dict[str, str]) -> None:
        """Creates `ServerGroup` with specified server prefix from Redis.
        If `ServerGroup exists, method does nothing.
        """
        if self.server_group_exists(prefix):
            return
        self.redis.sadd('servergroups', prefix)
        self.redis.hmset(f'servergroups.{prefix}', data)

    @staticmethod
    def generate_random_port() -> int:
        """Returns random port."""
        return randint(25000, 26000)

    def next_available_port(self) -> int:
        """Gets next available non-conflicting port (not between ten of any existing ports)"""
        port = self.generate_random_port()
        while self.get_if_port_conflicts(port):
            port = self.generate_random_port()
        return port

    def get_available_minecraft_servers(self) -> Iterator[str]:
        """Returns Iterator of ALL cached Minecraft servers.
        ServerStatus is a cached ServerGroup for online servers.
        """
        yield from self.redis.scan_iter('serverstatus.minecraft.*.*')

    def get_server_groups(self) -> Iterator[str]:
        """Returns Iterator of ServerGroups keys."""
        yield from self.redis.scan_iter('servergroups.*')

    def iterate_minecraft_servers_by_group(self, group: str, region: Region) -> Iterator[str]:
        """Returns Iterator of matching MinecraftServer keys by region.
        If region == `Region.ALL`, returns under all regions."""
        if region == Region.ALL:
            yield from self.redis.scan_iter(f'serverstatus.minecraft.{Region.US.value}.{group}-*')
            yield from self.redis.scan_iter(f'serverstatus.minecraft.{Region.EU.value}.{group}-*')
        else:
            yield from self.redis.scan_iter(f'serverstatus.minecraft.{region.value}.{group}-*')

    def get_if_minecraft_server_exists(self, server_name: str, region: Region) -> bool:
        """Returns if MinecraftServer exists in the Redis cache."""
        return self.redis.get(f'serverstatus.minecraft.{region.value}.{server_name}') is not None

    def get_server_group_dict(self, group: str) -> dict[str, str]:
        """Returns Json dictionary of ServerGroup from Redis."""
        group = group.replace('servergroups.', '')
        res = self.redis.hgetall(f'servergroups.{group}')
        if res is None:
            return {}
        return json.loads(str(res).replace("'", '"'))

    def get_server_status_dict(self, server_name: str, region: Region) -> dict[str, str]:
        """Returns Json dictionary of ServerStatus from Redis."""
        server_key = f'serverstatus.minecraft.{region.value}.{server_name}'
        if server_name.count('.') == 3:
            server_key = server_name
        res = self.redis.get(server_key)
        if res is None:
            return {}
        return json.loads(str(res).replace("'", '"'))

    @classmethod
    def create_session(cls) -> Self:
        """Creates a RedisRepository session using default connection information.
        
        Defaults: 
        - Address: 127.0.0.1
        - Port: 6379

        Change these in config/`config.toml`
        """

        create_config_if_not_exists()
        with open(CONFIG_PATH, 'r') as fp:
            data = toml.load(fp).get('redis_user', None)
        address, port = data.get('redis_address', '127.0.0.1'), data.get('redis_port', 6379)
        return cls(address, port)


@contextmanager
def get_redis_repo() -> Iterator[RedisRepository]:
    """For quick function call in `RedisRepository`. 
    Closes session immediately after result is retrieved.
    """
    repository = RedisRepository.create_session()
    try:
        yield repository
    finally:
        repository.close_connection()

