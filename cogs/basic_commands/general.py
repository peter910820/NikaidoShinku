import discord, os
from discord import app_commands
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name= "test", description="你覺得他會回你甚麼?")
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Your user name:{interaction.user}")

    @app_commands.command(name= "id", description="check user id.")
    async def id(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Your user ID:{interaction.user.id}")

    @app_commands.command(name= "exit", description="關閉機器人")
    async def exit(self, interaction: discord.Interaction):
        await interaction.response.send_message(f'正在關閉機器人...')
        await self.bot.close()

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(General(bot), guild= None)