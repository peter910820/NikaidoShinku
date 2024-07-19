import discord, os
from discord import app_commands
from discord.ext import commands
from pytube import Playlist, YouTube

class YoutubePlayerV3r(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.forbidden_char = ['/','\\',':','*','?','"','<','>',"|"]
        self.play_queue, self.title_queue = [], []
        self.pause_flag = False
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
        youtube_url = self.url_format(youtube_url)
        if youtube_url.startswith('https://www.youtube.com/playlist?list='):
            if interaction.user.voice == None:
                await interaction.response.send_message('使用者還沒進入語音頻道呦')
            elif self.bot.voice_clients == []:
                await interaction.response.send_message(f"Your URL is {youtube_url}")
                await interaction.user.voice.channel.connect()
                await self.change_status_music()
                await self.handle_playlist(youtube_url)

                if not self.bot.voice_clients[0].is_playing():
                    title = self.play_queue[0]['music_object'].title
                    music = self.play_queue[0]['music_object']
                    try:
                        music.streams.filter().get_lowest_resolution().download(filename=f"{self.song_path}/{title}.mp3")
                    except:
                        for f in self.forbidden_char:
                            title = title.replace(f,' ')
                        music.streams.filter().get_lowest_resolution().download(filename=f"{self.song_path}/{title}.mp3")
                    self.bot.voice_clients[0].play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable=self.ffmpeg_path, source=f"{self.song_path}/{title}.mp3"), volume= 0.1), after = lambda _ : self.after_song_interface(interaction))
                else:
                    await interaction.response.send_message(f'歌曲已加入排序: 歌單URL為{youtube_url}')
            else:
                await self.handle_playlist(youtube_url)
                if not self.bot.voice_clients[0].is_playing():
                    if not self.pause_flag:
                        title = self.play_queue[0]['music_object'].title
                        music = self.play_queue[0]['music_object']
                        try:
                            music.streams.filter().get_lowest_resolution().download(filename=f"{self.song_path}/{title}.mp3")
                        except:
                            for f in self.forbidden_char:
                                title = title.replace(f,' ')
                            music.streams.filter().get_lowest_resolution().download(filename=f"{self.song_path}/{title}.mp3")                  
                        self.bot.voice_clients[0].play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable=self.ffmpeg_path, source=f"{self.song_path}/{title}.mp3"), volume= 0.1), after = lambda _ : self.after_song_interface(interaction))
                else:
                    await interaction.response.send_message(f'歌曲已加入排序: 歌單URL為{youtube_url}')
                        
        elif youtube_url.startswith('https://www.youtube.com/'):
            pass
        else:
            print('error')

    async def after_song(self, interaction):
        print(interaction)
        self.play_queue.pop(0)
        self.clean(self)
        if len(self.play_queue) > 0:
            title = self.play_queue[0]['music_object'].title
            music = self.play_queue[0]['music_object']
            try:
                music.streams.filter().get_lowest_resolution().download(filename=f"{self.song_path}/{title}.mp3")
            except:
                for f in self.forbidden_char:
                    title = title.replace(f," ")
                music.streams.filter().get_lowest_resolution().download(filename=f"{self.song_path}/{title}.mp3")
            self.bot.voice_clients[0].play(discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(executable=self.ffmpeg_path, source=f"{self.song_path}/{title}.mp3"), volume= 0.1), after = lambda _ : self.after_song_interface(interaction))
        else:
            self.clean(self)
            game = discord.Game("ブルーアーカイブ -Blue Archive-")
            await self.bot.change_presence(activity=game, status=discord.Status.online) # status
            await interaction.response.send_message("已播放完歌曲")
            print("已播放完歌曲")

    def after_song_interface(self, interaction):
        self.bot.loop.create_task(self.after_song(interaction))

    async def handle_playlist(self, youtube_url: str) -> None:
        url_parse = Playlist(youtube_url)
        print(url_parse.video_urls)
        self.play_queue.extend([{'url': i, 'music_object': YouTube(i)} for i in url_parse.video_urls])
        # for p in url_parse.video_urls:
        #     self.play_queue.append(p)
        #     url_parse = YouTube(p)
        #     self.title_queue.append(url_parse.title)

    async def change_status_music(self) -> None:
        music = discord.Activity(type=discord.ActivityType.listening, name = 'Youtube的音樂')
        await self.bot.change_presence(activity=music, status=discord.Status.online)

    # @app_commands.command(name= "list", description= "查詢歌曲清單")       
    # async def list(self, interaction: discord.Interaction) -> None:
    #     if len(self.play_queue) == 0:
    #         await interaction.response.send_message('播放清單目前為空呦')
    #     else:
    #         playlist_check = f"```\n播放清單剩餘歌曲: {len(self.play_queue)}首\n"
    #         for index, t in enumerate(self.title_queue['music_object'].title, start=1):
    #             playlist_check += f"{index}. {t}\n"
    #             if len(playlist_check) >= 500:
    #                 playlist_check += " ...還有很多首"
    #                 break
    #         playlist_check += "```"
    #         print(self.play_queue)
    #         await interaction.response.send_message(playlist_check)


    def url_format(self, youtube_url: str) -> str:
        if youtube_url.startswith('https://www.youtube.com/'):
            return youtube_url
        elif youtube_url.startswith('https://music.youtube.com/'):
            return youtube_url.replace('music', 'www')
        elif youtube_url.startswith('https://youtube.com/'):
            return youtube_url.replace('https://youtube', 'https://www.youtube')
        else:
            return 'error'
        
    def clean(self, interaction):
        try:
            for file in os.scandir(self.song_path):
                if file.path[-4:] == ".mp3":
                    os.remove(file.path)
        except:
            pass
        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(YoutubePlayerV3r(bot), guild= None)