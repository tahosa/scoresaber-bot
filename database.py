from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, IntegerField, SQL
import logging
import config
from typing import List

_LOG = logging.getLogger('database')

logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

cfg = config.Config('server.cfg')

db = SqliteDatabase(cfg['database'])

'''
Base database model so we don't have to duplicate this Meta
'''
class BaseModel(Model):
    class Meta:
        database = db

'''
Represents a player. Links Steam, Discord, and ScoreSaber IDs
'''
class Player(BaseModel):
    steam_id = CharField(primary_key=True)
    discord_id = CharField(unique=True)
    scoresaber_id = CharField(unique=True)

'''
Individual song record. Only one per player ever exists and is updated when new high scores are recorded
'''
class Score(BaseModel):
    song_name = CharField()
    player = ForeignKeyField(Player, backref='player')
    score = IntegerField()
    
    class Meta:
        constraints = [SQL('UNIQUE(song_name, player_id)')]

'''
Actual class for interacting with the database
'''
class Database:
    '''
    Initialize the database object. Creates tables if necessary.
    '''
    def __init__(self):
        if not db.table_exists('player'):
            db.create_tables([Player, Score])

    '''
    Get the list of all players
    '''
    def get_players(self) -> List[Player]:
        with db:
            return Player.select()

    '''
    Create a new player in the database
    '''
    def create_player(self, steam_id: str, discord_id: str, scoresaber_id: str) -> None:
        with db:
            Player.create(steam_id=steam_id, discord_id=discord_id, scoresaber_id=scoresaber_id)
            return Player.get_by_id(steam_id)
