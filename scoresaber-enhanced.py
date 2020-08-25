import asyncio
import json
import logging
import pickle
import time

import aiohttp
import config
import discord
from discord.ext import commands, tasks
import requests

from database import Database

_LOG = logging.getLogger('scoresaber')
_LOG.setLevel(logging.DEBUG)

_HANDLER = logging.StreamHandler()
_HANDLER.addFilter(logging.Filter(name = 'scoresaber'))
_HANDLER.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.getLogger().addHandler(_HANDLER)


cfg = config.Config('server.cfg')
scoresaber_url = 'https://new.scoresaber.com/api'

client = discord.Client()
database = Database()

# @tasks.loop(seconds=60.0)
# async def score_update():
#     channel = client.get_channel(cfg['channel'])


@client.event
async def on_message(message):
    if message.author == client.user or message.channel.id != cfg['channel']:
        return

    if message.content.lower().startswith('hello bot'):
        await message.channel.send('Hewwo uwu')

    if message.content.lower().startswith('!list'):
        players = [player.steam_id for player in database.get_players()]
        await message.channel.send(f'Player list: {", ".join(players)}')

    if message.content.lower().startswith('!register'):
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
                            database.create_player(steam_id, player['playerId'], discord_id)
                            response = f'{steam_id} registered!'
                        except Exception as ex:
                            _LOG.exception(ex)
                            response = f'Failed to register {steam_id}. {ex}'
                            
                        _LOG.info(response)
                        await message.channel.send(response)

                if r.status == 404:
                    await message.channel.send(f'Player "{steam_id}" not found')
        

@client.event
async def on_ready():
    _LOG.info(f'We have logged in as {client.user.name}')
    # score_update.start()


client.run(cfg['bot_token'])
