import discord
import livestream_poller
import commands
import time
import json
import time

# True means currently live, False means currently not live
twitch_channels = {}
youtube_channels = {}
output_channel = None
next_time = 0
wait_time = 120 # in seconds
config = None

try:
    with open("streamspam.json") as f:
        config = json.load(f)
        if "twitch_channels" in config:
            for channel in config["twitch_channels"]:
                twitch_channels[channel] = False
        if "youtube_channels" in config:
            for channel in config["youtube_channels"]:
                youtube_channels[channel] = False
        if "output_channel" in config:
            output_channel = int(config["output_channel"])
        if "wait_time" in config:
            wait_time = int(config["wait_time"])
except:
    print("Couldn't load streamspam.json")

client = None

@commands.registerEventHandler(name="ssyoutube")
async def addYoutubeChannel(triggerMessage):
    if "youtube_channels" not in config:
        config["youtube_channels"] = []

    channel = triggerMessage.content.split(" ")[1].split("/")[-1]
    if channel not in config["youtube_channels"]:
        config["youtube_channels"].append(channel)
        youtube_channels[channel] = False
        await triggerMessage.channel.send(f"Added youtube channel {channel}")
        with open("streamspam.json", "w+") as f:
            json.dump(config, f)
    else:
        await triggerMessage.channel.send(f"{channel} already added")

@commands.registerEventHandler(name="sstwitch")
async def addTwitchChannel(triggerMessage):
    if "twitch_channels" not in config:
        config["twitch_channels"] = []

    channel = triggerMessage.content.split(" ")[1].split("/")[-1]
    if channel not in config["twitch_channels"]:
        config["twitch_channels"].append(channel)
        twitch_channels[channel] = False
        await triggerMessage.channel.send(f"Added twitch channel {channel}")
        with open("streamspam.json", "w+") as f:
            json.dump(config, f)
    else:
        await triggerMessage.channel.send(f"{channel} already added")

@commands.registerEventHandler(triggerType="\\timeTick", name="pollstreams")
async def pollstreams():
    global next_time
    global output_channel

    if time.time() < next_time:
        return

    print("polling live channels")
    next_time = time.time() + wait_time

    if isinstance(output_channel, int):
        # resolve channel id to channel object
        output_channel = client.get_channel(output_channel)

    for channel in twitch_channels.keys():
        live = livestream_poller.pollTwitchStatus(channel)
        # if they're live now and they weren't before, post in the channel
        if live and not twitch_channels[channel]:
            metadata = livestream_poller.getTwitchMetadata(channel)
            if metadata is None: # no yt-dlp to fetch metadata, just post link
                await output_channel.send(livestream_poller.createTwitchPollRoute(channel))
            else:
                # make an EMBED
                desc = metadata["description"]
                desc += "\n\n" + livestream_poller.createTwitchPollRoute(channel)
                embed = discord.Embed(title=metadata["uploader"], url=livestream_poller.createTwitchPollRoute(channel), description=desc, color=discord.Colour.from_rgb(100, 65, 165))
                embed.set_image(url=metadata["thumbnail"])
                await output_channel.send(embed=embed)

        twitch_channels[channel] = live

    for channel in youtube_channels.keys():
        err, result = livestream_poller.pollLivestreamStatus(channel)
        live = False
        if err is None:
            live = result.live == livestream_poller.STREAM_STATUS.LIVE

        # if they're live now and they weren't before, post in the channel
        if live and not youtube_channels[channel]:
            await output_channel.send(livestream_poller.createPollRoute(channel))

        youtube_channels[channel] = live
