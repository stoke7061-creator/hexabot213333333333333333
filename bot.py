import asyncio
import os
import random

import discord
from discord import app_commands

# On Railway, set a variable named DISCORD_TOKEN. For running on your PC,
# you can paste the token in place of PASTE_YOUR_BOT_TOKEN_HERE instead.
TOKEN = os.environ.get("DISCORD_TOKEN", "MTU3NTM0MzIxNzI2NjkxNzM3OA.GqcmzM.FYo1GvUcnC1cimANJTKsvvTxHK0G2QEOOoJqLw")
TOKEN = TOKEN.strip().strip('"').strip("'").strip()  # removes stray spaces/quotes

JOIN_MESSAGE = (
    "Inv 15 pepole or friends, for gilla mods!!\n"
    "they have to join for it to count\n"
    "https://discord.gg/mp7AFvFgf3"
)

intents = discord.Intents.default()
intents.members = True  # needs "Server Members Intent" enabled in the Developer Portal


print(f"Starting bot... token loaded: {len(TOKEN)} characters, {TOKEN.count('.')} dots", flush=True)


class Bot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_connect(self):
        print("Connected to Discord gateway.", flush=True)

    async def on_ready(self):
        # Sync the slash command to every server the bot is in (shows up instantly)
        for guild in self.guilds:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
        print(f"Logged in as {self.user} - ready. In {len(self.guilds)} server(s).", flush=True)

    async def on_guild_join(self, guild):
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

    async def on_member_join(self, member: discord.Member):
        if member.bot:
            return
        try:
            await member.send(JOIN_MESSAGE)
        except (discord.Forbidden, discord.HTTPException):
            pass  # their DMs are closed


client = Bot()


@client.tree.command(name="dm-all", description="DM everyone in the server")
@app_commands.describe(message="The message to send to everyone")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
async def dm_all(interaction: discord.Interaction, message: str):
    await interaction.response.send_message("Started sending DMs...", ephemeral=True)

    sent = 0
    failed = 0
    async for member in interaction.guild.fetch_members(limit=None):
        if member.bot:
            continue
        try:
            await member.send(message)
            sent += 1
        except (discord.Forbidden, discord.HTTPException):
            failed += 1
        await asyncio.sleep(random.uniform(2, 4))  # slow on purpose to avoid rate limits/bans

    summary = f"Done! Sent: {sent} | Failed (DMs closed): {failed}"
    try:
        await interaction.followup.send(summary, ephemeral=True)
    except discord.HTTPException:
        # interaction expired (>15 min), DM the result instead
        await interaction.user.send(summary)


@dm_all.error
async def dm_all_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("Admins only.", ephemeral=True)
    else:
        raise error


client.run(TOKEN)
