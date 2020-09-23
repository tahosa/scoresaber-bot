import logging

import aiohttp
import requests
import discord
from peewee import IntegrityError

from database import Database, Difficulty, Score
from updater import ScoreUpdater

_LOG = logging.getLogger('scoresaber')
scoresaber_url = 'https://new.scoresaber.com/api'

'''
Format a score for printing
'''
def _format_score(score: Score) -> str:
    result = f'{score.song_name}'

    if score.song_artist:
        result += f' by {score.song_artist}'

    if score.song_mapper:
        result += f' [map by {score.song_mapper}]'

    result += f' ({Difficulty(score.difficulty)}): {score.score}'

    return result


class MessageHandler:
    database: Database = None
    updater: ScoreUpdater = None

    def __init__(self, database: Database, updater: ScoreUpdater):
        self.database = database
        self.updater = updater

    '''
    List the steam IDs of all registered players
    '''
    async def player_list(self, message):
        players = [player.steam_id for player in self.database.get_players()]
        await message.channel.send(f'Player list: {", ".join(players)}')

    '''
    Register a new player
    '''
    async def register(self, message) -> bool:
        cmd = message.content.split(' ')
        if len(cmd) < 2 or len(cmd) > 3:
            await message.channel.send(f'Invalid register command. Usage: `!register <steam_id> [discord#id]`')
            return

        steam_id = cmd[1]

        # If we were given a discord ID, look them up; they must be in the server users
        if len(cmd) == 3:
            (name, discriminator) = cmd[2].split('#')
            discord_user = discord.utils.get(message.guild.members, name=name, discriminator=discriminator)
            discord_id = discord_user.id
        else:
            discord_id = None

        async with aiohttp.ClientSession() as session:
            _LOG.debug(f'Looking up `{steam_id}`')
            url = f'{scoresaber_url}/players/by-name/{steam_id}'
            _LOG.debug(f'GET {url}')
            async with session.get(url) as r:
                _LOG.debug(f'Response from server. Code {r.status}')

                if r.status == 200:
                    result = await r.json()
                    if len(result['players']) > 0:
                        player = result['players'][0]
                        try:
                            self.database.create_player(steam_id, discord_id, player['playerId'])
                            response = f'{player["playerName"]} registered!'
                            _LOG.info(response)
                            await message.channel.send(response)
                            return True
                        except IntegrityError as ex:
                            _LOG.exception(ex)
                            response = f'{steam_id} is already registerd.'
                            await message.channel.send(response)
                            return False
                        except Exception as ex:
                            _LOG.exception(ex)
                            response = f'Failed to register {steam_id}. {ex}'
                            await message.channel.send(response)
                            return False

                if r.status == 404:
                    await message.channel.send(f'Player "{steam_id}" not found')
                    return False

    '''
    Get the list of scores for a player by steam ID
    '''
    async def get_player_scores(self, message):
        cmd = message.content.split(' ')
        if(len(cmd) < 2):
            await message.channel.send(f'Invalid scores command. Usage: `!scores <steam_id> [limit]`')

        limit = 10
        if(len(cmd) > 2):
            limit = cmd[2]

        scores = self.database.get_player_scores(cmd[1], limit)

        if not scores:
            await message.channel.send(f'No scores found for {cmd[1]}')
            return

        reply = f'Top scores for {cmd[1]}: \n'
        for score in scores:
            reply += f'{_format_score(score)}\n'

        await message.channel.send(reply)

    '''
    Update the list of high scores
    '''
    async def update(self, message):
        force = '--force' in message.content
        quiet = '--quiet' in message.content

        new_records = await self.updater.update(force)
        await message.channel.send('High Scores Updated!')

        response = ''
        if len(new_records) > 0:
            for record in new_records:
                response += f'{record}\n'
        else:
            response = 'No new high scores.'

        if len(response) > 2000 or quiet:
            await message.channel.send(f'{len(new_records)} new high scores.')
        else:
            await message.channel.send(response)

    '''
    Get a list of scores matching a search
    '''
    async def search_top(self, message):
        search = message.content[len('!top'):].strip()
        if len(search) < 1:
            await message.channel.send('No search string specified')
            return

        results = self.database.get_top_search(search)

        response = f'Top scores for songs matching `{search}`:\n'
        for score in results:
            response += f'{score.player.steam_id}: {_format_score(score)}\n'

        if len(response) > 2000:
            await message.channel.send(f'Too many results to display ({len(results)}). Try a narrower search.')

        else:
            await message.channel.send(response)
