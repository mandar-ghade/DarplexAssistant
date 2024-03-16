from redis import Redis

class RedisAssistant:
    def __init__(self, host: str, port: int) -> None:
        self.redis = Redis(host=host, port=port, db=0, decode_responses=True)
    
    def server_group_exists(self, prefix: str) -> bool:
        return len(list(self.redis.scan_iter(f'servergroups.{prefix}'))) > 0

# ra = RedisAssistant('127.0.0.1', 6379)

# print(ra.server_group_exists('TF'))
