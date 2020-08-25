import asyncio
import json
import logging
import pickle
import time

import aiohttp
import config
import discord
from discord.ext import commands, tasks

from database import Database
from message_handler import MessageHandler

_LOG = logging.getLogger('scoresaber')
_LOG.setLevel(logging.DEBUG)

_HANDLER = logging.StreamHandler()
_HANDLER.addFilter(logging.Filter(name = 'scoresaber'))
_HANDLER.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logging.getLogger().addHandler(_HANDLER)


cfg = config.Config('server.cfg')

client = discord.Client()
database = Database()
mh = MessageHandler(database)

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
        await mh.player_list(message)

    if message.content.lower().startswith('!register'):
        await mh.register(message)

    if message.content.lower().startswith('!scores'):
        await mh.get_scores(message)
        

@client.event
async def on_ready():
    _LOG.info(f'We have logged in as {client.user.name}')
    # score_update.start()


client.run(cfg['bot_token'])
