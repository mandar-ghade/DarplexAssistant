from typing import Self
from redis import Redis
from random import randint

class RedisAssistant:
    def __init__(self, host: str, port: int) -> None:
        self.redis = Redis(host=host, port=port, db=0, decode_responses=True)
    
    def server_group_exists(self, prefix: str) -> bool:
        for _ in self.redis.scan_iter(f'servergroups.{prefix}'):
            return True
        return False

    def next_available_port(self) -> int:
        port = randint(25000, 26000)
        while any(port - 10 <= int(self.redis.hget(group, 'portSection')) <= port + 10
                  for group in self.redis.scan_iter('servergroups.*')):
            port = randint(25000, 26000)
        return port

    @classmethod
    def create_session(cls) -> Self:
        return cls('127.0.0.1', 6379)


print(RedisAssistant.create_session().next_available_port())


# ra = RedisAssistant('127.0.0.1', 6379)

# print(ra.server_group_exists('TF'))
