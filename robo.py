#!/usr/bin/env python3
"""
A discord bot for automatic ARMA3 event management.
"""

import json
import discord
import asyncio

from discord import http

########################################
# -------- LOAD CONFIGURATION -------- #
########################################
"""
{
    "token": <INSERT DISCORD TOKEN>,
    "event": {
        "channel": "Events",
    }
}
"""
with open('config.json') as jf:
    config = json.load(jf)
    
if not config:
    print("Unable to load settings.")
    exit(1)

########################################
# -------- UTILITY FUNCTIONS  -------- #
########################################


@asyncio.coroutine
def fixed_edit_channel(client, channel, **options):
    # get current parameters
    keys = ['name', 'topic', 'position', 'parent_id']
    for key in keys:
        if key not in options:
            options[key] = getattr(channel, key)

    payload = { k: v for k, v in options.items() }
    yield from client.http.request(http.Route('PATCH', '/channels/{channel_id}', channel_id=channel.id), json=payload)


async def parse_params(params):
    params.split()
    del params[0]
    return params

########################################
# ------- INIT DISCORD CLIENT  ------- #
########################################

client = discord.Client()


async def create_event(name, date, briefing, slots):
    for server in client.servers:
        # find parent channel (config['event']['channel'])
        parent = None
        for chIt in server.channels:
            if chIt.name == config['event']['channel']:
                parent = chIt
                break
                
        if parent:
            chan = await client.create_channel(server, name)
            await asyncio.sleep(1)
            if chan:
                await fixed_edit_channel(client, chan, position=1, parent_id=parent.id)
                await client.send_message(chan, date)
                await client.send_message(chan, briefing)
                await client.send_message(chan, slots)
                
        else:
            print("Error: Unable to find event '{}' parent channel '{}'.".format(name, config['event']['channel']))
            continue


@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

    # create a new event and posts event
    if message.content.startswith('!create-event'):
        # parse parameters
        params = parse_params(message.content)
        # enough parameters?
        if len(params) == 4:
            await create_event(params[0], params[1], params[2], params[3])
        else:
            await client.send_message(message.channel, 'Please create an event with "!create-event <name> <date> <briefing> <slotting>')

    # create voice channel
    if message.content.startswith('!voice'):
        # parse parameters
        params = parse_params(message.content)
        # rejoin into string
        name = "".join(params)
        await asyncio.sleep(1)
        # duplicate
        for server in client.servers:
            # find parent category 'Voice'
            parent = None
            for chIt in server.channels:
                if chIt.name == 'Voice':
                    parent = chIt
                    break

        chan = await client.create_channel(server, name, type=discord.ChannelType.voice)
        if chan and parent:
            await fixed_edit_channel(client, chan, position=5, parent_id=parent.id)


@client.event
async def on_ready():
    print('Logged in as {}/{}'.format(client.user.name, client.user.id))
    print('------')

client.run(config['token'])
