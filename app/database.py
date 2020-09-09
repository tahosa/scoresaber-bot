import logging
from typing import List
from enum import Enum

import config
from peewee import (SQL, CharField, ForeignKeyField, IntegerField, Model,
                    SqliteDatabase, fn)

_LOG = logging.getLogger('scoresaber')

# Uncomment these to see DB queries
# logger = logging.getLogger('peewee')
# logger.addHandler(logging.StreamHandler())
# logger.setLevel(logging.DEBUG)

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
    discord_id = CharField(null=True)
    scoresaber_id = CharField(unique=True, null=False)


'''
Individual song record. Only one per player ever exists and is updated when new high scores are recorded
'''
class Score(BaseModel):
    song_name = CharField(null=False)
    song_artist = CharField()
    song_mapper = CharField()
    song_hash = CharField(null=False)
    difficulty = IntegerField(null=False)
    player = ForeignKeyField(Player, backref='player')
    score = IntegerField(null=False)

    class Meta:
        constraints = [SQL('UNIQUE(song_hash, difficulty, player_id)')]

'''
Translate numeric difficulty as tracked by scoresaber
'''
class Difficulty(Enum):
    EASY = 1
    NORMAL = 3
    HARD = 5
    EXPERT = 7
    EXPERT_PLUS = 9

    '''
    Outputs for use in format() and f-strings
    '''
    def __format__(self, format_spec):
        if self.value == 1:
            return 'Easy'
        elif self.value == 3:
            return 'Normal'
        elif self.value == 5:
            return 'Hard'
        elif self.value == 7:
            return 'Expert'
        elif self.value == 9:
            return 'Expert+'
        else:
            return Enum.__format__(self, format_spec)


'''
Class for interacting with the database
'''
class Database:
    db = db

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
        return Player.select()

    '''
    Create a new player in the database
    '''
    def create_player(self, steam_id: str, discord_id: str, scoresaber_id: str) -> Player:
        Player.create(steam_id=steam_id, discord_id=discord_id, scoresaber_id=scoresaber_id)
        return Player.get_by_id(steam_id)

    '''
    Create or update a high score for a specific song by a player.

    If a record doesn't exist, create a new high score for a song. If a record exists,
    update it if the new score is higher. Returns true if the score was created or updated,
    false otherwise.
    '''
    def update_score(self,
                     player: str,
                     song_hash: str,
                     difficulty: Difficulty,
                     score: int,
                     song_name: str,
                     song_artist: str = '',
                     song_mapper: str = '') -> Score:

        # Find if there is already a score for this player in the table
        old_score = Score.select() \
            .where((Score.player == player) & (Score.song_hash == song_hash) & (Score.difficulty == difficulty)) \
            .order_by(Score.score.desc()) \
            .limit(1)

        if len(old_score): # Score already recorded
            _LOG.debug(f'Found old score of {old_score[0].score} for {player} on {song_name}')
            if score > old_score[0].score: # Is it higher than what we have?
                old_score[0].score = score
                old_score[0].save()
                return old_score[0]

            # Score wasn't higher than one already in the database
            return None

        else: # New song
            return Score.create(song_hash=song_hash,
                            player=player,
                            score=score,
                            difficulty=difficulty,
                            song_name=song_name,
                            song_artist=song_artist,
                            song_mapper=song_mapper)


    '''
    Get the list of scores for a specific player
    '''
    def get_player_scores(self, player: str, limit: int = 100) -> List[Score]:
        return Score.select().where(Score.player == player).order_by(Score.score.desc()).limit(limit)


    '''
    Get the current high-score records
    '''
    def get_high_scores(self) -> List[Score]:
        return Score.select(Score, Player, fn.Max(Score.score).alias('high_score')) \
                    .join(Player) \
                    .group_by(Score.song_hash, Score.difficulty) \
                    .prefetch(Player)


    '''
    Get the scores for a particular song
    '''
    def get_song_scores(self, song_hash: str, difficulty: Difficulty) -> List[Score]:
        return Score.select() \
            .join(Player) \
            .where((Score.song_hash == song_hash) & (Score.difficulty == difficulty)) \
            .order_by(Score.score.desc()) \
            .prefetch(Player)
