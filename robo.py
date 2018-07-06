#!/usr/bin/env python3
"""
A discord bot for automatic ARMA3 event management.
"""

import json
import discord
import asyncio

########################################
# -------- LOAD CONFIGURATION -------- #
########################################
"""
{
    "token": <INSERT DISCORD TOKEN>,
    "server": <INSERT SERVER ID>,
    "event": {
        "params": 4,
        "channel": "events",
    }
}
"""
with open('config.json') as jf:
    config = json.load(jf)
    
if not config:
    print("Unable to load settings.")
    exit(1)


########################################
# ------- INIT DISCORD CLIENT  ------- #
########################################

client = discord.Client()

async def create_event(name, date, briefing, slots):
    for server in client.servers:
        chan = await client.create_channel(server, name)
        await asyncio.sleep(1)
        await client.move_channel(chan, 7)
        await client.send_message(chan, date)
        await client.send_message(chan, briefing)
        await client.send_message(chan, slots)

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
        #parse parameters
        params = message.content.split()
        del params[0]
        if len(params) == config['event']['params']:
            await create_event(params[0], params[1], params[2], params[3])
        else:
            await client.send_message(message.channel, 'Please create an event with "!create-event <name> <date> <briefing> <slotting>')

@client.event
async def on_ready():
    print('Logged in as {}/{}'.format(client.user.name, client.user.id))
    print('------')

client.run(config['token'])