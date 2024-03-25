import json
import os
from redis import Redis
from random import randint
from typing import Iterator, Self
import toml


DEFAULT_TOML_CONF: dict[str, dict[str, str | int]] = {
    'redis_user': {
        'redis_address': '127.0.0.1',
        'redis_port': 6379,
    },
    'server_monitor_options': {
        'ram': '6000',
        'servers_directory': 'home/mineplex/servers',
        'jars_directory': 'home/mineplex/jars',
        'world_zip_folder_directory': 'home/mineplex/worlds',
    }
}


class RedisAssistant:
    def __init__(self, host: str, port: int) -> None:
        self.redis = Redis(host=host, port=port, db=0, decode_responses=True)
    
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

    @classmethod
    def create_session(cls) -> Self:
        """
        Creates a RedisAssistant session using default connection information.
        
        Defaults: 
        - Address: 127.0.0.1
        - Port: 6379

        Change these in `config.toml`

        """
        if not os.path.exists('config.toml'):
            with open('config.toml', 'w') as fp:
                toml.dump(DEFAULT_TOML_CONF, fp)
        with open('config.toml', 'r') as fp:
            data = toml.load(fp).get('redis_user', None)
        address, port = data.get('redis_address', '127.0.0.1'), data.get('redis_port', 6379)
        return cls(address, port)

