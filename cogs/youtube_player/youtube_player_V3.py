import discord, os
from discord import app_commands
from discord.ext import commands
from pytube import YouTube, Playlist

class YoutubePlayer(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.forbidden_char = ['/','\\',':','*','?','"','<','>',"|"]
        self.play_queue = []
        self.title_queue = []
        self.ffmpeg_path = "./ffmpeg/bin/ffmpeg.exe"
        self.song_path = "./music_tmp/"

        self.play_prefix = "https://www.youtube.com/"
        self.playlist_prefix = ["https://www.youtube.com/playlist?list=", "https://youtube.com/playlist?list="]
    
    @app_commands.command(name= "join", description= "加入語音頻道")
    async def join(self, interaction: discord.Interaction) -> None:
        if interaction.user.voice == None:
            await interaction.response.send_message("未加入頻道")
        elif self.bot.voice_clients == []:
            voiceChannel = interaction.user.voice.channel
            await voiceChannel.connect()
            music = discord.Activity(type=discord.ActivityType.listening, name = "Yotube的音樂")
            await self.bot.change_presence(activity=music, status=discord.Status.online) # status
        else:
            await interaction.response.send_message("已加入頻道")

    @app_commands.command(name= "leave", description= "離開語音頻道")
    async def leave(self, interaction: discord.Interaction) -> None:
        if self.bot.voice_clients != []:
            await self.bot.voice_clients[0].disconnect()
            game = discord.Game("ブルーアーカイブ -Blue Archive-")
            await self.bot.change_presence(activity=game, status=discord.Status.online) # status
            await interaction.response.send_message("已離開頻道")
        else:
            await interaction.response.send_message("目前沒有在任何頻道")

    @app_commands.command(name= "play", description= "播放音樂")
    async def play(self, interaction: discord.Interaction, youtube_url: str) -> None:
        await interaction.response.send_message(f"Your URL is {youtube_url}")
        if youtube_url.startswith(self.playlist_prefix[0]) or youtube_url.startswith(self.playlist_prefix[1]):
            if interaction.user.voice == None:
                await interaction.response.send_message('使用者還沒進入語音頻道呦')
            elif self.bot.voice_clients == []:
                voiceChannel = interaction.user.voice.channel
                await voiceChannel.connect()
                music = discord.Activity(type=discord.ActivityType.listening, name = 'Yotube的音樂')
                await self.bot.change_presence(activity=music, status=discord.Status.online)
                self.clean(self) # delete all mp3 file
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
                    self.bot.voice_clients[0].play(discord.FFmpegOpusAudio(executable=self.ffmpeg_path, source=f"{self.song_path}/{title}.mp3"), after = lambda _ : self.after_song(self))
            else:
                if not self.bot.voice_clients[0].is_playing():
                    await interaction.response.send_message("我已經在語音頻道了呦")
                else:
                    url_parse = Playlist(youtube_url)
                    print(url_parse.video_urls)
                    for p in url_parse.video_urls:
                        self.play_queue.append(p)
                        url_parse = YouTube(p)
                        self.title_queue.append(url_parse.title)   

        elif youtube_url.startswith(self.play_prefix):
            if interaction.user.voice == None:
                await interaction.response.send_message('使用者還沒進入語音頻道呦')
            elif self.bot.voice_clients == []:
                voiceChannel = interaction.user.voice.channel
                await voiceChannel.connect()
                music = discord.Activity(type=discord.ActivityType.listening, name = 'Yotube的音樂')
                await self.bot.change_presence(activity=music, status=discord.Status.online)
                self.clean(self) # delete all mp3 file
                if not self.bot.voice_clients[0].is_playing():
                    try:
                        music = YouTube(youtube_url)
                        self.play_queue.append(youtube_url)
                        self.title_queue.append(music.title)
                        print(self.play_queue)
                        title = music.title
                        music.streams.filter().get_lowest_resolution().download(filename=f"{self.song_path}/{title}.mp3")
                        self.bot.voice_clients[0].play(discord.FFmpegOpusAudio(executable=self.ffmpeg_path, source=f"{self.song_path}/{title}.mp3"), after = lambda _ : self.after_song(self))
                    except OSError as err:
                        for f in self.forbidden_char:
                            title = title.replace(f," ")
                        music.streams.filter().get_lowest_resolution().download(filename=f"{self.song_path}/{title}.mp3")
                        self.bot.voice_clients[0].play(discord.FFmpegOpusAudio(executable=self.ffmpeg_path, source=f"{self.song_path}/{title}.mp3"), after = lambda _ : self.after_song(self))
                    except:
                        await interaction.response.send_message("找不到歌曲!")
            else:
                if not self.bot.voice_clients[0].is_playing():
                    await interaction.response.send_message("我已經在語音頻道了呦, 目前狀態為閒置狀態")
                else:
                    try:
                        music = YouTube(youtube_url)
                        self.play_queue.append(youtube_url)
                        self.title_queue.append(music.title)
                    except:
                        await interaction.response.send_message("找不到歌曲!")
        else:
            await interaction.response.send_message("找不到歌曲!")

    def after_song(self):
        self.play_queue.pop(0)
        self.title_queue.pop(0)
        self.clean(self)
        if self.play_queue != []:
            music = YouTube(self.play_queue[0])
            title = music.title
            try:
                music.streams.filter().get_lowest_resolution().download(filename=f"{self.song_path}/{title}.mp3")
            except:
                for f in self.forbidden_char:
                    title = title.replace(f," ")
                music.streams.filter().get_lowest_resolution().download(filename=f"{self.song_path}/{title}.mp3")
            self.bot.voice_clients[0].play(discord.FFmpegOpusAudio(executable=self.ffmpeg_path, source=f"{self.song_path}/{title}.mp3"), after = lambda _ : self.after_song(self))

    @app_commands.command(name= "now", description= "現在播放歌曲")
    async def now(self, interaction: discord.Interaction) -> None:
        if len(self.title_queue) == 0:
            await interaction.response.send_message('播放清單目前為空呦')
        else:
            tmp_str = f"現在歌曲: **{self.title_queue[0]}**"
            await interaction.response.send_message(tmp_str)

    @app_commands.command(name= "skip", description= "跳過歌曲")
    async def skip(self, interaction: discord.Interaction, count: int= 1) -> None:
        if self.bot.voice_clients[0] != []:
            if self.bot.voice_clients[0].is_playing():
                self.bot.voice_clients[0].stop()
                if count > 1:
                    count -= 1
                    for _ in range(0, count):
                        self.play_queue.pop(0)
                        self.title_queue.pop(0)
                await interaction.response.send_message('歌曲已跳過')
            # else:
            #     await interaction.response.send_message.send('沒有歌曲正在播放呦')
        else:
            await interaction.response.send_message('我還沒加入語音頻道呦')

    @app_commands.command(name= "list", description= "查詢歌曲清單")       
    async def list(self, interaction: discord.Interaction) -> None:
        if len(self.play_queue) == 0:
            await interaction.response.send_message('播放清單目前為空呦')
        else:
            playlist_check = f"```\n播放清單剩餘歌曲: {len(self.play_queue)}首\n"
            for index, t in enumerate(self.title_queue, start=1):
                playlist_check += f"{index}. {t}\n"
                if len(playlist_check) >= 500:
                    playlist_check += " ...還有很多首"
                    break
            playlist_check += "```"
            print(self.play_queue)
            await interaction.response.send_message(playlist_check)

    def clean(self):
        try:
            for file in os.scandir(self.song_path):
                if file.path[-4:] == ".mp3":
                    os.remove(file.path)
        except:
            pass

    @app_commands.command(name= "pause", description= "暫停歌曲")  
    async def pause(self, interaction):
        if self.bot.voice_clients[0].is_playing():
            self.bot.voice_clients[0].pause()
            await interaction.response.send_message('歌曲已暫停')
        else:
            await interaction.response.send_message('沒有歌曲正在播放呦')

    @app_commands.command(name= "resume", description= "繼續撥放歌曲")  
    async def resume(self, interaction):
        if self.bot.voice_clients[0].is_paused():
            self.bot.voice_clients[0].resume()
            await interaction.response.send_message('歌曲已繼續播放')
        else:
            await interaction.response.send_message('沒有歌曲正在暫停呦')
    
    #handling error
    @play.error
    async def play_error(self, interaction: discord.Interaction, error: discord.DiscordException) -> None:
        await interaction.response.send_message(error)

    @now.error
    async def now_error(self, interaction: discord.Interaction, error: discord.DiscordException) -> None:
        await interaction.response.send_message(error)

    @skip.error
    async def skip_error(self, interaction: discord.Interaction, error: discord.DiscordException) -> None:
        await interaction.response.send_message(error)

    @list.error
    async def list_error(self, interaction: discord.Interaction, error: discord.DiscordException) -> None:
        await interaction.response.send_message(error)

    @pause.error
    async def pause_error(self, interaction: discord.Interaction, error: discord.DiscordException) -> None:
        await interaction.response.send_message(error)

    @resume.error
    async def resume_error(self, interaction: discord.Interaction, error: discord.DiscordException) -> None:
        await interaction.response.send_message(error)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(YoutubePlayer(bot), guild= None)