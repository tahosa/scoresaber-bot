import logging
from typing import List

import aiohttp
import requests

from database import Database, Score, Difficulty

_LOG = logging.getLogger('scoresaber')
scoresaber_url = 'https://new.scoresaber.com/api'

class ScoreUpdater:
    database: Database = None

    def __init__(self, database: Database):
        self.database = database


    '''
    Query scoresaber for new scores and update the database. Returns a list of new records.
    '''
    async def update(self) -> List[str]:
        players = self.database.get_players()
        new_high_scores = []

        for player in players:
            async with aiohttp.ClientSession() as session:
                _LOG.debug(f'Fetching new scores for {player.steam_id}')
                async with session.get(f'{scoresaber_url}/player/{player.scoresaber_id}/scores/recent/1') as r:
                    if r.status == 200:
                        json = await r.json()
                        scores = json['scores']
                        _LOG.debug(f'Found {len(scores)} to parse')
                        for score in scores:
                            new_high = self.database.update_score(
                                player=player.steam_id,
                                song_hash=score['songHash'],
                                song_name=score['songName'],
                                song_artist=score['songAuthorName'],
                                song_mapper=score['levelAuthorName'],
                                difficulty=score['difficulty'],
                                score=score['score'],
                            )

                            if new_high:
                                new_high_scores.append(new_high)

        if len(new_high_scores):
            response: List[str] = []
            for score in new_high_scores:
                score_string = ''

                # Add the mention if there is a discord ID
                if score.player.discord_id:
                    score_string = f'<@{score.player.discord_id}>'
                else:
                    score_string = f'{score.player.steam_id}'

                score_string += f' set a new high score of {score.score} on {score.song_name} by {score.song_artist} ({Difficulty(score.difficulty)})'
                response.append(score_string)

            if len(response) == 0: # New PBs, but no overall new highs
                return []

            return response

        else:
            return []
