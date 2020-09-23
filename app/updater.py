import logging
from typing import List

import aiohttp
import requests

from database import Database, Score, Difficulty

_LOG = logging.getLogger('scoresaber')
scoresaber_url = 'https://new.scoresaber.com/api'

class ScoreUpdater:
    database: Database = None
    _current_high: List[Score] = []

    def __init__(self, database: Database):
        self.database = database
        self._current_high = self.database.get_high_scores()


    '''
    Query scoresaber for new scores and update the database. Returns a list of new records.
    '''
    async def update(self, force_all=False) -> List[str]:
        players = self.database.get_players()
        new_pbs = []

        for player in players:
            async with aiohttp.ClientSession() as session:
                _LOG.debug(f'Fetching new scores for {player.steam_id}')
                page = 1
                while True:
                    async with session.get(f'{scoresaber_url}/player/{player.scoresaber_id}/scores/recent/{page}') as r:
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

                                if new_high and new_high not in new_pbs:
                                    new_pbs.append(new_high)
                            page += 1

                        else:
                            _LOG.debug(f'Bad return status {r.status} {r.reason}')
                            break

                    if not force_all:
                        break

        if len(new_pbs):
            new_overall = self.database.get_high_scores()

            # Get a list of scores where there is a new player in the top slot
            # The iterator tracks by ID, and since we update existing rows if a player beats their
            # own high score it won't appear in this list
            updated_overall = [value for value in new_overall if value not in self._current_high]

            # Save the updated list now we don't need the old scores
            self._current_high = new_overall

            response: List[str] = []
            for score in new_pbs:
                score_string = ''

                # Add the mention if there is a discord ID
                if score.player.discord_id:
                    score_string = f'<@{score.player.discord_id}>'
                else:
                    score_string = score.player.steam_id

                if score in updated_overall: # Beat another player
                    song_leaderboard = self.database.get_song_scores(score.song_hash, score.difficulty)

                    if len(song_leaderboard) > 1:
                        score_string += ' beat '

                        old_leader = song_leaderboard[1]
                        if old_leader.player.discord_id:
                            score_string += f'<@{old_leader.player.discord_id}>'
                        else:
                            score_string += old_leader.player.steam_id

                        score_string += f'\'s high score of {old_leader.score} with a new high score of {score.score}'

                    else: # Shouldn't ever get here, but just in case
                        score_string += f' set a new high score of {score.score}'

                else: # Beat their own high score
                    score_string += f' set a new high score of {score.score}'

                score_string += f' on {score.song_name}'

                if score.song_artist:
                    score_string += f' by {score.song_artist}'

                if score.song_mapper:
                    score_string += f' [map by {score.song_mapper}]'

                score_string += f' ({Difficulty(score.difficulty)})'
                response.append(score_string)

            if len(response) == 0: # New PBs, but no overall new highs
                return []

            return response

        else:
            return []
