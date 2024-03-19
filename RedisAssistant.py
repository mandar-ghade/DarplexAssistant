import json
import os
from redis import Redis
from random import randint
from typing import Iterable, Iterator, Optional, Self
import time
import toml
from Region import Region


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

    def get_server_statuses(self) -> Iterator[str]:
        """Returns Iterator of ServerStatus (servergroup caches)"""
        for group in self.redis.scan_iter('serverstatus.minecraft.US.*'):
            yield group

    def get_server_group_uptime(self) -> Iterator[tuple[dict[str, str | int], bool]]:
        """Returns Iterator of a tuple of ServerStatus (dict) and is_online (bool)"""
        for group in self.get_server_statuses():
            group = self.redis.get(group)
            group  = json.loads(str(group))
            is_online = (time.time() * 1000 - int(group.get('_currentTime'))) <= 10000
            yield (group, is_online)

    def _get_region_by_str(self, region_str: str) -> Region:
        """
        Returns matching Region object to region_str.
        Defaults to Region.ALL.
        (Will rewrite this to be non-class method in future)
        """
        for region in Region:
            if region.value != region_str:
                continue
            return region
        return Region.ALL #failsafe

    def convert_dict_to_server_group_insertable(self, prefix: str) -> dict[str, Region | str | bool | int]:
        """
        Does opposite of convert_to_str in ServerGroup
        (Will rewrite this to be non-class method in future)
        """
        input_dict: dict[str, str] = self._fetch_server_group(prefix)
        sg_dict = dict[str, Region | str | bool | int]()
        regions = ('US', 'EU', 'ALL')
        booleans = ('true', 'false')
        for key, value in input_dict.items():
            if value in regions:
                value = self._get_region_by_str(value)
            elif value in booleans:
                value = value == 'true'
            elif str(value).isdigit():
                value = int(value)
            sg_dict[key] = value
        return sg_dict


    def _fetch_server_group(self, prefix: str) -> dict[str, str]:
        """ 
        Fetches Redis key by prefix and returns dict[str, str].
        DO NOT USE THIS. THIS IS AN INTERNAL method.

        Refer to self.convert_dict_to_server_group_insertable(prefix) instead.
        """
        return self.redis.hgetall(f'servergroups.{prefix}')

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


# ra = RedisAssistant.create_session()
# for group, is_online in ra.get_server_group_uptime():
#    print(group, is_online)
