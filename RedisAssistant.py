from redis import Redis
from random import randint
from typing import Self
import json

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

    @classmethod
    def create_session(cls) -> Self:
        """
        Creates a RedisAssistant session using default connection information.
        
        Defaults: 
        - Address: 127.0.0.1
        - Port: 6379

        Change these in `config.json`

        """
        with open('config.json', 'r') as fp:
            data = json.load(fp)
        address, port = data.get('redisAddress'), data.get('redisPort')
        return cls(address, port)

