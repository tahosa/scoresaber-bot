import logging

import aiohttp
import requests

from database import Database

_LOG = logging.getLogger('scoresaber')

scoresaber_url = 'https://new.scoresaber.com/api'

class MessageHandler:
    database = None
    def __init__(self, database):
        self.database = database

    '''
    List the steam IDs of all registered players
    '''
    async def player_list(self, message):
        players = [player.steam_id for player in self.database.get_players()]
        await message.channel.send(f'Player list: {", ".join(players)}')

    '''
    Register a new player
    '''
    async def register(self, message):
        cmd = message.content.lower().split(' ')
        if len(cmd) != 3:
            await message.channel.send(f'Invalid register command. Usage: `!register <steam_id> <discord_id>`')
            return

        steam_id = cmd[1]
        discord_id = cmd[2]

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
                        except Exception as ex:
                            _LOG.exception(ex)
                            response = f'Failed to register {steam_id}. {ex}'
                            
                        _LOG.info(response)
                        await message.channel.send(response)

                if r.status == 404:
                    await message.channel.send(f'Player "{steam_id}" not found')
    
    '''
    Get the list of scores for a player by steam ID
    '''
    async def get_scores(self, message):
        cmd = message.content.lower().split(' ')
        if(len(cmd) < 2):
            await message.channel.send(f'Invalid scores command. Usage: `!scores <steam_id> [limit]')
        
        limit = 100
        if(len(cmd) > 2):
            limit = cmd[2]

        scores = self.database.get_scores(cmd[1], limit)

        if not scores:
            await message.channel.send(f'No scores found for {cmd[1]}')
            return

        reply = f'Top scores for {cmd[1]}: \n'
        for score in scores:
            reply += f'{score.song_name}: {score.score}'

        await message.channel.send(reply)
