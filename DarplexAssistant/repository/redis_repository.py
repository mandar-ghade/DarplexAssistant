import json
from redis import Redis
from random import randint
from typing import Iterator, Self
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

    def next_available_port(self) -> int:
        """Gets next available non-conflicting port (not between ten of any existing ports)"""
        port = randint(25000, 26000)
        while any(port - 10 <= int(self.redis.hget(group, 'portSection')) <= port + 10
                  for group in self.redis.scan_iter('servergroups.*')):
            port = randint(25000, 26000)
        return port

    def get_available_minecraft_servers(self) -> Iterator[str]:
        """
        Returns Iterator of cached Minecraft servers.
        ServerStatus is a cached ServerGroup for online servers.
        """
        for group in self.redis.scan_iter('serverstatus.minecraft.US.*'):
            yield group

    def get_server_groups(self) -> Iterator[str]:
        """Returns Iterator of ServerGroups keys."""
        for group in self.redis.scan_iter('servergroups.*'):
            yield group

    def get_if_minecraft_server_exists(self, server_name: str) -> bool:
        """Returns if MinecraftServer exists in the Redis cache."""
        return self.redis.get(f'serverstatus.minecraft.US.{server_name}') is not None

    def get_server_group_dict(self, group: str) -> dict[str, str]:
        """Returns Json dictionary of ServerGroup from Redis."""
        group = group.replace('servergroups.', '')
        res = self.redis.get(f'servergroups.{group}')
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
        """
        Creates a RedisRepository session using default connection information.
        
        Defaults: 
        - Address: 127.0.0.1
        - Port: 6379

        Change these in `config.toml`

        """

        create_config_if_not_exists()
        with open(CONFIG_PATH, 'r') as fp:
            data = toml.load(fp).get('redis_user', None)
        address, port = data.get('redis_address', '127.0.0.1'), data.get('redis_port', 6379)
        return cls(address, port)

