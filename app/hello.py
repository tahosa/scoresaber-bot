import discord
import config
cfg = config.Config('server.cfg')


client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user or message.channel.id != cfg['channel']:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(cfg['bot_token'])