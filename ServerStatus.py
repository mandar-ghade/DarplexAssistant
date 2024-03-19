from dataclasses import dataclass


@dataclass 
class ServerStatus:
    name: str
    group: str
    motd: str
    player_count: int
    max_player_count: int
    tps: int
    ram: int
    max_ram: int
    public_address: str
    port: int
    donors_online: int
    start_up_date: int
    current_time: int


