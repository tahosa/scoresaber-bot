import logging
from typing import List

import config
from peewee import (SQL, CharField, ForeignKeyField, IntegerField, Model,
                    SqliteDatabase)

_LOG = logging.getLogger('scoresaber')

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
    def create_player(self, steam_id: str, discord_id: str, scoresaber_id: str) -> Player:
        with db:
            Player.create(steam_id=steam_id, discord_id=discord_id, scoresaber_id=scoresaber_id)
            return Player.get_by_id(steam_id)

    '''
    Create or update a high score for a specific song by a player.
    
    If a record doesn't exist, create a new high score for a song. If a record exists,
    update it if the new score is higher.
    '''
    def update_score(self, player: str, song_name: str, score: int) -> int:
        with db:
            # Find if there is already a score for this player in the table
            old_score = Score.select() \
                .where((Score.player == player) & (Score.song_name == song_name)) \
                .order_by(Score.score.desc()) \
                .limit(1)

            if len(old_score): # Score already recorded
                _LOG.debug(f'Found old score of {old_score[0].score} for {player} on {song_name}')
                if old_score[0].score < score: # Is it higher than what we have?
                    old_score[0].update(score=score).execute()
                    return score
                
                # Score wasn't higher than one already in the database
                return old_score[0].score

            else: # New song
                Score.create(song_name=song_name, player=player, score=score)
                return score


    '''
    Get the list of scores for a specific player
    '''
    def get_scores(self, player: str, limit: int = 100) -> List[Score]:
        with db:
            Score.select().where(Score.player == player).order_by(Score.score.desc()).limit(limit)
