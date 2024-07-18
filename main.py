import discord, os
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

class SyaroBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix= "\\",
            intents= intents
        )

    async def setup_hook(self):
        await self.load_extension("cogs.error_handler")
        await self.load_extension("cogs.basic_commands.general")
        await self.load_extension("cogs.youtube_player.youtube_player_V3")
        await self.load_extension("cogs.youtube_player.youtube_player_V3R")
        # await self.load_extension("cogs.song_quiz")
        await bot.tree.sync(guild= None)

    async def on_ready(self):
        print(f"{self.user} is online.") # print('logging in as {0.user}'.format(bot))
        print(f"delay time: {str(round(self.latency*1000, 2))}ms.")
        game = discord.Game("正在研究人生道理") # status
        await self.change_presence(status=discord.Status.online, activity=game) # change status to game

bot = SyaroBot()
bot.run(os.getenv("TOKEN"))