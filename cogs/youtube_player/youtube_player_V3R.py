import discord, os
from discord import app_commands
from discord.ext import commands
from pytube import Playlist, YouTube

class YoutubePlayerV3r(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.forbidden_char = ['/','\\',':','*','?','"','<','>',"|"]
        self.play_queue = []
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
        if await self.handle_connect(interaction):
            if youtube_url.startswith('https://www.youtube.com/playlist?list='):
                try:
                    await self.handle_playlist(youtube_url)
                except Exception as e:
                    print(f'error={e}')
                    await interaction.response.send_message("❌意外狀況發生,請檢察log❌")
                    return
                if not self.bot.voice_clients[0].is_playing():
                    await interaction.response.send_message(f'歌曲已加入: 歌單URL為{youtube_url}呦 🌟')
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
                    await interaction.response.send_message(f'歌曲已加入排序: 歌單URL為{youtube_url}呦 🌟')
            elif youtube_url.startswith('https://www.youtube.com/'):
                try:
                    self.play_queue.append({'url': youtube_url, 'music_object': YouTube(youtube_url)})
                except Exception as e:
                    print(f'error={e}')
                    await interaction.response.send_message("❌意外狀況發生,請檢察log❌")
                    return
                if not self.bot.voice_clients[0].is_playing():
                    await interaction.response.send_message(f'歌曲已加入: 歌曲URL為{youtube_url}呦 🌟')
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
                    await interaction.response.send_message(f'歌曲已加入排序: 歌曲URL為{youtube_url} 呦🌟')
            else:
                await interaction.response.send_message("找不到歌曲呦!❌")
        else:
            await interaction.response.send_message('使用者還沒進入語音頻道呦❌')

    async def after_song(self, interaction: discord.Interaction):
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
            await interaction.response.send_message("🌟已播放完歌曲🌟")
            print("🌟已播放完歌曲🌟")

    def after_song_interface(self, interaction: discord.Interaction):
        self.bot.loop.create_task(self.after_song(interaction))
    
    async def handle_connect(self, interaction: discord.Interaction) -> bool:
        if interaction.user.voice == None:
            return False
        elif self.bot.voice_clients == []:
            await interaction.user.voice.channel.connect()
            await self.change_status_music()
            return True
        else:
            return True

    async def handle_playlist(self, youtube_url: str) -> None:
        url_parse = Playlist(youtube_url)
        print(url_parse.video_urls)
        self.play_queue.extend([{'url': i, 'music_object': YouTube(i)} for i in url_parse.video_urls])

    async def change_status_music(self) -> None:
        music = discord.Activity(type=discord.ActivityType.listening, name = 'Youtube的音樂')
        await self.bot.change_presence(activity=music, status=discord.Status.online)

    @app_commands.command(name= "list", description= "查詢歌曲清單")       
    async def list(self, interaction: discord.Interaction) -> None:
        if len(self.play_queue) == 0:
            await interaction.response.send_message('播放清單目前為空呦')
        else:
            playlist_check = f"```\n播放清單剩餘歌曲: {len(self.play_queue)}首\n"
            for index, t in enumerate(self.play_queue['music_object'].title, start=1):
                playlist_check += f"{index}. {t}\n"
                if len(playlist_check) >= 500:
                    playlist_check += " ...還有很多首"
                    break
            playlist_check += "```"
            print(self.play_queue)
            await interaction.response.send_message(playlist_check)

    @app_commands.command(name= "now", description= "現在播放歌曲")
    async def now(self, interaction: discord.Interaction) -> None:
        if len(self.play_queue) == 0:
            await interaction.response.send_message('播放清單目前為空呦')
        else:
            tmp_str = f"現在歌曲: **{self.play_queue['music_object'].title}**"

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
                await interaction.response.send_message('歌曲已跳過')
            else:
                await interaction.response.send_message.send('沒有歌曲正在播放呦')
        else:
            await interaction.response.send_message('我還沒加入語音頻道呦')

    @app_commands.command(name= "pause", description= "暫停歌曲")  
    async def pause(self, interaction) -> None:
        if self.bot.voice_clients[0].is_playing():
            self.bot.voice_clients[0].pause()
            self.pause_flag = True
            await interaction.response.send_message('歌曲已暫停')
        else:
            await interaction.response.send_message('沒有歌曲正在播放呦')

    @app_commands.command(name= "resume", description= "繼續撥放歌曲")  
    async def resume(self, interaction) -> None:
        if self.bot.voice_clients[0].is_paused():
            self.bot.voice_clients[0].resume()
            self.pause_flag = False
            await interaction.response.send_message('歌曲已繼續播放')
        else:
            await interaction.response.send_message('沒有歌曲正在暫停呦')

    def url_format(self, youtube_url: str) -> str:
        if youtube_url.startswith('https://www.youtube.com/'):
            return youtube_url
        elif youtube_url.startswith('https://music.youtube.com/'):
            return youtube_url.replace('music', 'www')
        elif youtube_url.startswith('https://youtube.com/'):
            return youtube_url.replace('https://youtube', 'https://www.youtube')
        else:
            return 'error'
        
    def clean(self, interaction): #interaction???
        try:
            for file in os.scandir(self.song_path):
                if file.path[-4:] == ".mp3":
                    os.remove(file.path)
        except PermissionError:
            print('file is open now!')
#handling error-------------------------------------------------------------------------------------#
    @now.error
    async def now_error(self, interaction: discord.Interaction, error: discord.DiscordException) -> None:
        await interaction.response.send_message(error)

    @skip.error
    async def skip_error(self, interaction: discord.Interaction, error: discord.DiscordException) -> None:
        await interaction.response.send_message(error)

    @list.error
    async def list_error(self, interaction: discord.Interaction, error: discord.DiscordException) -> None:
        await interaction.response.send_message(error) 
#setup---------------------------------------------------------------------------------------------#  
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(YoutubePlayerV3r(bot), guild= None)