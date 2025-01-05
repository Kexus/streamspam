import discord
import pkgutil
import sys
import json
import asyncio

import inspect
import time
import threading

import commands

import streamspam

loaded = False

# AAAAAAAIIIIIIIIIII IM TIME LOOPING AGAIN
def timeLoop(asyncLoop):
    while True:
        time.sleep(1)
        try:
            asyncLoop.call_soon_threadsafe(asyncio.ensure_future, commands.executeEvent(triggerType="\\timeTick"))
        except RuntimeError:
            print("!!!!!!!!!!! Event loop is dead, trying to make a new one")
            print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncLoop.call_soon_threadsafe(asyncio.ensure_future, commands.executeEvent(triggerType="\\timeTick"))


    
if __name__ == "__main__":
    print("Loading config")
    with open('config.json', 'r') as configfile:
        config = json.loads(configfile.read())

    print("Config loaded")
    client = discord.Client()
    # permissions.client = client
    commands.client = client
    streamspam.client = client

    def listen():
        @client.event
        async def on_reaction_add(reaction, user):
            await commands.executeEvent(triggerType="\\reactionAdded", triggerMessage=reaction.message, reaction=reaction, user=user)
            
        @client.event
        async def on_reaction_remove(reaction, user):
            await commands.executeEvent(triggerType="\\reactionRemoved", triggerMessage=reaction.message, reaction=reaction, user=user)
        
        @client.event
        async def on_message(message):
            await commands.executeEvent(triggerType="\\message", triggerMessage=message)

            if message.author.id != client.user.id:#we ignore our own messages
                await commands.executeEvent(triggerType="\\messageNoBot", triggerMessage=message)
                #print("Got message")
                #commands
                if message.content.startswith("$"):
                    commandName = message.content.split()[0][1:]#TODO:im not sure if this should be done in *this* part of the code, but then how?
                    print("Got command " + commandName)
                    await commands.executeEvent(triggerType="\\command", name=commandName, triggerMessage=message)
                return

        @client.event
        async def on_channel_update(before, after):
            await commands.executeEvent(triggerType="\\channelUpdate", before=before, after=after)

        @client.event
        async def on_ready():
            global loaded
            # await client.change_presence(status=discord.Status.dnd)
            # print("Logged in as")
            # print(client.user.name)
            # print(client.user.id)
            # print("------")

            if not loaded:

                loop = asyncio.get_event_loop()
                timeTickThread = threading.Thread(target=timeLoop, kwargs={"asyncLoop":loop})
                timeTickThread.daemon = True
                timeTickThread.start()
                loaded = True
                
            # await client.change_presence(status=discord.Status.online)

        @client.event
        async def on_error(event, *args, **kwargs):
            await client.close()
            sys.exit(event)

        @client.event
        async def on_message_edit(before, after):
            await commands.executeEvent(triggerType="\\messageEdit", before=before, after=after)
            
        loaded = False
        print(config["DiscordToken"])
        client.run(config["DiscordToken"])
    
    print("Logging in")
    listen()#hey, listen,
