scoresaber-bot
==============

This is a Discord bot for tracking scoresaber high scores among your friends!

Installing
----------

TBD - Probably docker

Configuring
-----------

Create a config file named `server.cfg` with the following:

```
bot_token: '<bot_token>'
channel: <channel_id>
database: 'scores.db'
```

Use the bot token from your Discord app page, and the numeric channel ID from the
Discord developer extensions (right-click the channel and choose 'Copy ID'). You are
free to rename the database file whatever you want. If it is empty, it will be created on the first run.

Developing
----------

The recommended use is to set up to use `pyenv` or `virtualenv` (or both) to manage
the python dependencies.

```shell
pyenv virtualenv python3 scoresaber-bot
pyenv activate scoresaber-bot
pip install -r requirements.txt
```

This assumes you have configured pyenv correctly and set up the shim wrappers on your
`$PATH`

### Debugging
Run the application with `python scoresaber-enhance.py`
