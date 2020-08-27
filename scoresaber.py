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
from updater import ScoreUpdater
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
updater = ScoreUpdater(database)
mh = MessageHandler(database, updater)

@tasks.loop(seconds=cfg['update_interval'])
async def score_update():
    _LOG.debug('Checking for new scores')
    channel = client.get_channel(cfg['channels'][0])
    with database.db:
        new_scores = await updater.update()

    _LOG.debug(f'Found {len(new_scores)} new high scores')
    if len(new_scores) > 0:
        for score in new_scores:
            await channel.send(score)


@client.event
async def on_message(message):
    # Ignore messages from the bot, or from channels that are not being watched
    if message.author == client.user or message.channel.id not in  cfg['channels']:
        return

    _LOG.debug('Opening database')
    with database.db:

        content = message.content.lower()
        _LOG.debug('Begin parsing message')
        
        # Power User functions
        if f'{message.author.name}#{message.author.discriminator}' in cfg['power_users']:
            if content.startswith('!update'):
                await mh.update(message)

            if content.startswith('!register'):
                if await mh.register(message):
                    await mh.update(message)

        if content.startswith('hello bot'):
            await message.channel.send('Hewwo uwu')

        if content.startswith('!list'):
            await mh.player_list(message)

        if content.startswith('!scores'):
            await mh.get_player_scores(message)
        

@client.event
async def on_ready():
    _LOG.info(f'We have logged in as {client.user.name}')
    score_update.start()


client.run(cfg['bot_token'])
