from GameOptions import GameOptions

class Game:
    Micro = GameOptions('MB')
    MixedArcade = GameOptions('MIN', 8, 24)
    Draw = GameOptions('DMT', 5, 8) 
    Build = GameOptions('BLD', 8, 12)
    TurfWars = GameOptions('TF', 8, 16)
    SpeedBuilders = GameOptions('SB', 4, 8)
    HideSeek = GameOptions('BH', 12, 24)
    CakeWarsDuos = GameOptions('CW2', 10, 16)
    CakeWarsTeams = GameOptions('CW4', 10, 16)
    SurvivalGames = GameOptions('HG', 12, 24)
    SurvivalGamesTeams = GameOptions('SG2', 12, 24)
    Skywars = GameOptions('SKY', 8, 12)
    SkywarsTeams = GameOptions('SKY2', 8, 12)
    Bridges = GameOptions('BR', 20, 40)
    MineStrike = GameOptions('MS', 8, 16)
    Smash = GameOptions('SSM', 4, 6)
    SmashTeams = GameOptions('SSM2', 4, 6)
    ChampionsDOM = GameOptions('DOM', 8, 10)
    ChampionsCTF = GameOptions('CTF', 10, 16)
    Clans = GameOptions('Clans', 1, 50, False, 
                        'clans.zip', 'Clans.jar', 
                        'plugins/Clans', False, False, 
                        False, 'dedicated', False, 
                        True, False, False, 
                        False, False, True, 
                        False, False, True, 
                        True, True, True, 
                        False, True, False)
    ClansHub = GameOptions('ClansHub', 1, 50, False, 
                        'clanshub.zip', 'ClansHub.jar', 
                        'plugins/ClansHub', False, False, 
                        False, 'dedicated', False, 
                        True, False, False, 
                        False, False, True, 
                        False, False, True, 
                        True, True, True, 
                        False, True, False)

