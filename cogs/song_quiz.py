import discord, os, asyncio, json, time
from discord import app_commands
from discord.ext import commands
from pytube import YouTube, Playlist

class SongQuiz(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.forbidden_char = ['/','\\',':','*','?','"','<','>',"|"]
        self.play_queue = []
        self.title_queue = []
        self.ffmpeg_path = "./ffmpeg/bin/ffmpeg.exe"
        self.song_path = "./music_tmp/"

        self.play_prefix = ["https://www.youtube.com/", "https://music.youtube.com/", "https://youtube.com/"]
        self.playlist_prefix = ["https://www.youtube.com/playlist?list=", "https://music.youtube.com/playlist?list=",  "https://youtube.com/playlist?list="]

    @app_commands.command(name= "quizgame", description= "開始猜歌遊戲")
    async def play(self, interaction: discord.Interaction, youtube_url: str) -> None:
        await interaction.response.send_message(f"Your URL is {youtube_url}")
        if youtube_url.startswith(self.playlist_prefix[1]) or youtube_url.startswith(self.play_prefix[1]):
            youtube_url = youtube_url.replace("music.", "www.")

        if youtube_url.startswith(self.playlist_prefix[0]) or youtube_url.startswith(self.playlist_prefix[2]):
            if interaction.user.voice == None:
                await interaction.response.send_message('使用者還沒進入語音頻道呦')
            elif self.bot.voice_clients == []:
                voiceChannel = interaction.user.voice.channel
                await voiceChannel.connect()
                await self.change_status_music()
                url_parse = Playlist(youtube_url)
                print(url_parse.video_urls)
                for p in url_parse.video_urls:
                    self.play_queue.append(p)
                    url_parse = YouTube(p)
                    self.title_queue.append(url_parse.title)

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
                    await asyncio.sleep(5)
                    # 停止音乐播放
                    self.bot.voice_clients[0].stop()
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

        elif youtube_url.startswith(self.play_prefix[0]) or youtube_url.startswith(self.play_prefix[2]):
            if interaction.user.voice == None:
                await interaction.response.send_message('使用者還沒進入語音頻道呦')
            elif self.bot.voice_clients == []:
                voiceChannel = interaction.user.voice.channel
                await voiceChannel.connect()
                await self.change_status_music()
                if not self.bot.voice_clients[0].is_playing():
                    try:
                        music = YouTube(youtube_url)
                    except:
                        await interaction.response.send_message("找不到歌曲!")
                    try:
                        title = await self.song_handle(youtube_url, music)
                    except OSError as err:
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
                    try:
                        music = YouTube(youtube_url)
                        self.play_queue.append(youtube_url)
                        self.title_queue.append(music.title)
                    except:
                        await interaction.response.send_message("找不到歌曲!")
        else:
            await interaction.response.send_message("找不到歌曲!")

    async def after_song(self, interaction):
        print(interaction)
        self.play_queue.pop(0)
        self.title_queue.pop(0)
        self.clean(self)
        if len(self.play_queue) > 0:
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
            self.clean(self)
            game = discord.Game("ブルーアーカイブ -Blue Archive-")
            await self.bot.change_presence(activity=game, status=discord.Status.online) # status
            print("已播放完歌曲")

    #handle the same working----------------------------------------------------------------------------#

    async def change_status_music(self):
        music = discord.Activity(type=discord.ActivityType.listening, name = 'Yotube的音樂')
        await self.bot.change_presence(activity=music, status=discord.Status.online)
        self.clean(self) # delete all mp3 file
    
    async def song_handle(self, youtube_url, music):
        try:
            self.play_queue.append(youtube_url)
            self.title_queue.append(music.title)
            print(self.play_queue)
            title = music.title
            music.streams.filter().get_lowest_resolution().download(filename=f"{self.song_path}/{title}.mp3")
        except OSError as err:
            for f in self.forbidden_char:
                title = title.replace(f," ")
            music.streams.filter().get_lowest_resolution().download(filename=f"{self.song_path}/{title}.mp3")
        return title
    
    def after_song_interface(self, interaction):
        self.bot.loop.create_task(self.after_song(interaction))

    def clean(self, interaction):
        try:
            for file in os.scandir(self.song_path):
                if file.path[-4:] == ".mp3":
                    os.remove(file.path)
        except:
            pass

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SongQuiz(bot), guild= None)