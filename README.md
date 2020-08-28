scoresaber-bot
==============

This is a Discord bot for tracking scoresaber high scores among your friends!

Running
-------

The bot is set up to be run using Docker. To start, do the following:

1. [Create your server config file](#Configuring)
2. (Optional) Create an empty file for the database.
    * This is useful if you want the database to be re-used if you need to tear down the container for any reason, e.g. updating
3. Build the container with `docker build . -t scoresaber:latest`
    * Eventually it will be pushed to docker hub, but not yet
4. Start the container and mount the config and database files
    * `docker run -d --mount type=bind,source=/path/to/scores.db,target=/scoresaber/scores.db --mount type=bind,source=/path/to/server.cfg,target=/scoresaber/server.cfg scoresaber-bot:latest`
    * This command assumes you are using `scores.db` as the database name inside your server config. Update that mount if you are using something else.

Using
-----

There are currently 4 commands that can be used. The bot will only respond to these triggers in the channels specified in the server config [(see Configuring)](#Configuring)

#### `!register <steam_id> [discord#id]`

This adds a new user to the tracking database. For `steam_id` Use the complete, unique Steam ID. This is currently problematic if you have a steam ID that is a substring of one or more other steam IDs (e.g. `apple`) since the scoresaber API is a bulk search and may return multiple results.

`discord#id` is the server-unique name and discriminator code for that user in your server. The user must be in your server for the registration to work since the lookup is done on the server members. This is optional, but if specified will mention that user when they break a record.

#### `!update`

Force an update of the scores list. The server will automatically update the list when a new user is registered, and on the interval specified in the [(configuration file)](#Configuring).

#### `!list`

List the currently registered users

#### `!scores <steam_id> [limit]`

List a number of the top scores of the specified preregistered user, up to `limit`. Unlike the `!register` command, this command reads the local database for users and will exact-match the given `steam_id` instead of fuzzy-match/searching.

Configuring
-----------

Create a config file named `server.cfg` with the following:

```
bot_token: '<bot_token>'
channels: [<channel_id>, ...]
database: 'scores.db'
power_users: ['<discord#id>', ...]
update_interval: 60.0
```

#### `bot_token`

The bot token from your Discord app page as a quoted string. This is used to authenticate with Discord and start the bot.

#### `channels`

A list of all the numeric channel IDs you want to bot to listen in. You can get these from the Discord developer extensions (right-click the channel and choose 'Copy ID'). The first entry in the list will be the one where updated scores are posted automatically.

#### `database`

The name of the sqlite3 database file to use. You are free to rename the database file whatever you want. If it does not exist or is empty it will be created on the first run. If you want to reset the score tracking: stop the bot, delete the datbase file, and restart the bot.

#### `power_users`
A list of those users you wish to be able to register other users or force a manual update of the score database. The database is automatically updated when a new user is registered. They should be spefied using their server-specific name and discriminator in the format `user#discriminator`, e.g. `someUser#1234`.

#### `update_interval`

Time, in seconds, between checking the scoresaber API for new scores. The recommended interval is 1 minute (60.0 seconds) but you are free to specify any interval.

Developing
----------

The recommended use is to set up to use `pyenv` or `virtualenv` (or both) to manage the python dependencies. Currently, the bot has been developed and tested using python 3.8.

```shell
pyenv virtualenv python3 scoresaber-bot
pyenv activate scoresaber-bot
pip install -r requirements.txt
```

This assumes you have configured pyenv correctly and set up the shim wrappers on your `$PATH`

### Debugging

Run the application with `python3 app/scoresaber.py`. If you are using VS Code, a launch configuration has been provided.
