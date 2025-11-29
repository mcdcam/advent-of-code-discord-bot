from typing import Optional
from config import config
from leaderboard import fetch_images
from logging import warning
import discord
from discord import app_commands

async def respond_or_followup(interaction: discord.Interaction, **kwargs):
    if interaction.response.is_done():
        await interaction.followup.send(**kwargs)
    else:
        await interaction.response.send_message(**kwargs)

my_client = discord.Client(intents=discord.Intents.none())
tree = app_commands.CommandTree(my_client)

@my_client.event
async def on_ready():
    print(f"{my_client.user} is ready and online!")
    await tree.sync()

@tree.command()
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def leaderboard(interaction: discord.Interaction) -> None:
    await fetch_images(interaction.response)
    image = discord.File("./fetched_images/leaderboard.png")
    await respond_or_followup(interaction, file=image)

@tree.command()
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def podium(interaction: discord.Interaction) -> None:
    await fetch_images(interaction.response)
    image = discord.File("./fetched_images/podium.png")
    await respond_or_followup(interaction, file=image)

@tree.command()
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def graph(interaction: discord.Interaction) -> None:
    await fetch_images(interaction.response)
    image = discord.File("./fetched_images/graph.png")
    await respond_or_followup(interaction, file=image)

@tree.command()
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def delta(interaction: discord.Interaction, day: Optional[int]=None) -> None:
    await fetch_images(interaction.response)
    
    if day is not None:
        try:
            with open(f"./fetched_images/delta_day_{day}.png", "rb") as f:
                image = discord.File(f)
        except FileNotFoundError:
            warning(f"Delta image for day {day} not found")
            await interaction.response.send_message(f"Delta image for day {day} not found")
            return
    else:
        image = discord.File("./fetched_images/delta.png")

    await respond_or_followup(interaction, file=image)

my_client.run(config["DISCORD_TOKEN"])
