# Description
This is a simple music bot. It can be used to play and queue tracks from youtube (see Commands).
It can support multiple guilds (servers) at once and manages a queue for each guild separately.

## Commands

All of these commands only affect the bots behaviour in the guild in which they were typed.

> +play song

Joins the channel of the sender and plays the song. Song can be either search term or youtube link.

> +skip

Skips the current track and starts playing the next track in the queue (if not empty).

> +leave

Leaves the current voice channel.

> +pause

Pauses the current track.

> +resume

Resumes the current track.

> +stop

Clears the queue and stops playing the current track.

# Setup
## Dependencies

The first dependency is ffmpeg. It can be downloaded from https://www.ffmpeg.org/download.html. It also needs to be added to the system PATH.

Then there are two dependencies that can be installed via pip

> pip install discord

> pip install youtube_dl

## Configuring
First a application and bot must be made on the discord developer portal (https://discord.com/developers/applications).

Then to run your music bot with python the bot_token at the bottom of music_bot.py has to be replaced with your own bot token (gotten from the discord developer portal).

Alternatively instead of storing the token inside the music_bot.py file it can also be stored in a file called keys in this format: BOT_TOKEN=YOURTOKEN. The keys file should be placed in the same directory as the music_bot.py file.

# Running
To run navigate to the directory containing the music_bot.py file. Then run it via

> python music_bot.py

You might need to specify python version 3 in which case the following should suffice

> python music_bot.py
