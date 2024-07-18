import discord, os
from discord import app_commands
from discord.ext import commands
from pytube import Playlist, YouTube

class YoutubePlayerV3r(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.forbidden_char = ['/','\\',':','*','?','"','<','>',"|"]
        self.play_queue, self.title_queue = [], []
        self.ffmpeg_path = "./ffmpeg/bin/ffmpeg.exe"
        self.song_path = "./music_tmp/"

    @app_commands.command(name= "join", description= "加入語音頻道")
    async def join(self, interaction: discord.Interaction) -> None:
        if interaction.user.voice == None:
            await interaction.response.send_message("未加入頻道")
        elif self.bot.voice_clients == []:
            voiceChannel = interaction.user.voice.channel
            await voiceChannel.connect()
            await self.change_status_music()
        else:
            await interaction.response.send_message("已加入頻道")

    @app_commands.command(name= "leave", description= "離開語音頻道")
    async def leave(self, interaction: discord.Interaction) -> None:
        if self.bot.voice_clients != []:
            await self.bot.voice_clients[0].disconnect()
            await self.bot.change_presence(activity = discord.Game("ブルーアーカイブ -Blue Archive-"), status=discord.Status.online)
            await interaction.response.send_message("已離開頻道")
        else:
            await interaction.response.send_message("目前沒有在任何頻道")
        self.clean(self)

    @app_commands.command(name= "play", description= "播放音樂")
    async def play(self, interaction: discord.Interaction, youtube_url: str) -> None:
        await interaction.response.send_message(f"Your URL is {youtube_url}")

        youtube_url = self.url_format(youtube_url)

        if youtube_url.startswith('https://www.youtube.com/playlist?list='):
            if interaction.user.voice == None:
                await interaction.response.send_message('使用者還沒進入語音頻道呦')
            elif self.bot.voice_clients == []:
                await interaction.user.voice.channel.connect()
                await self.change_status_music()
                url_parse = Playlist(youtube_url)
                print(url_parse.video_urls)
                self.play_queue = [[i, YouTube(i).title] for i in url_parse.video_urls]
                # for p in url_parse.video_urls:
                #     self.play_queue.append(p)
                #     url_parse = YouTube(p)
                #     self.title_queue.append(url_parse.title)

                if not self.bot.voice_clients[0].is_playing():
                    music = YouTube(self.play_queue[0])
                    title = music.title
                    try:
                        music.streams.filter().get_lowest_resolution().download(filename=f"{self.song_path}/{title}.mp3")
                    except:
                        for f in self.forbidden_char:
                            title = title.replace(f," ")
                        music.streams.filter().get_lowest_resolution().download(filename=f"{self.song_path}/{title}.mp3")
                    self.bot.voice_clients[0].play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable=self.ffmpeg_path, source=f"{self.song_path}/{title}.mp3"), volume= 0.1), after = lambda _ : self.after_song_interface(interaction))
            else:
                if not self.bot.voice_clients[0].is_playing():
                    await self.change_status_music()
                    try:
                        music = YouTube(youtube_url)
                    except:
                        await interaction.response.send_message("找不到歌曲!")
                    title = await self.song_handle(youtube_url, music)                    
                    self.bot.voice_clients[0].play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable=self.ffmpeg_path, source=f"{self.song_path}/{title}.mp3"), volume= 0.1), after = lambda _ : self.after_song_interface(interaction))
                else:
                    url_parse = Playlist(youtube_url)
                    print(url_parse.video_urls)
                    for p in url_parse.video_urls:
                        self.play_queue.append(p)
                        url_parse = YouTube(p)
                        self.title_queue.append(url_parse.title)
                        
        elif youtube_url.startswith('https://www.youtube.com/'):
            pass
        else:
            print('error')

    def url_format(self, youtube_url: str) -> str:
        if youtube_url.startswith('https://www.youtube.com/'):
            return youtube_url
        elif youtube_url.startswith('https://music.youtube.com/'):
            return youtube_url.replace('music', 'www')
        elif youtube_url.startswith('https://youtube.com/'):
            return youtube_url.replace('https://youtube', 'https://www.youtube')
        else:
            return 'error'
        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(YoutubePlayerV3r(bot), guild= None)