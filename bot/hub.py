import discord
import youtube_dl
import yt_search
from discord.ext import commands, tasks
import ffmpeg
import re
from random import choice
import asyncio
import json
from tools import send_message, send_embed_message, Mypath
import time

# global ytdl
YTDL_OPTIONS = {
    # "options" : "--force-ipv4",
    'format':'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'logtostderr': False,
        # 'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0'
    }
# 'format': 'bestaudio/best',
#         'extractaudio': True,
#         'audioformat': 'mp3',
#         'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
#         'restrictfilenames': True,
#         'noplaylist': True,
#         'nocheckcertificate': True,
#         'ignoreerrors': True,
#         'logtostderr': False,
#         'quiet': True,
#         'no_warnings': True,
#         'default_search': 'auto',
#         'source_address': '0.0.0.0',

ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5'
}

ytdl = youtube_dl.YoutubeDL(YTDL_OPTIONS)


async def play_hub_song(hub, voice_client, url, priority = True):
    try:
        print("passage dans la connexion, try 1")
        if hub.voice_client == None:
            connection = await voice_client.connect()
            hub.set_voice_client(connection)
        else:
            connection = await hub.voice_client.connect()
            hub.set_voice_client(connection)
    except Exception as e1:
        try:
            print("passage dans la connexion, try 2")
            connection = await hub.author_voice_channel.connect()
            hub.set_voice_client(connection)
        except Exception as e2:
            print("le bot n'a pas réussi à se connecter")
            await send_embed_message(title = "Erreur Bot", description = "Erreur lors de la connexion du bot\ntapez **" + hub.cmd_prefix + "leave** pour reboot le bot")
            return
    #     try:
    #         print("passage dans la connexion de secours")
    #         connection = await hub.last_voice_client.connect()
    #         hub.set_voice_client(connection)
    #     except Exception as e:
    #         print("le bot est déjà connecté en voc")

    print("priorité de lecture -> " + "True" if priority == True else "False")
    if priority == True:
        hub.play(url)

class Song():
    def __init__(self, link = None, video = None):
        self.error = False
        if not video and link:
            video = ytdl.extract_info(link, download = False)
        if video and video["format"] and video["title"] and video["webpage_url"]:
            video_format = video["formats"][0]
            self.title = video["title"]
            self.url = video["webpage_url"]
            self.stream_url = video_format["url"]
        else:
            self.error = True


# class Yt_List():
#     def __init__(self, hub, client, link):

#         # guild_nb = get_guild_nb(guild_list, ctx.guild)
#         yt_list = ytdl.extract_info(link, download = False)
#         i = 0

#         for video in yt_list["entries"]:
#             song = Song(video = video)
#             if song.error == False and song.title and song.url and song.stream_url:
#                 if i == 0 and (not client or (client and not client.is_playing())):
#                     hub.current_song = song
#                 else:
#                     hub.musics_queue.append(song)
#                 i += 1
#             else:
#                 print("la musique " + str(i) + " a eu un problème")


class VabCommand():
    def __init__(self):
        #config
        with open(Mypath().bot + 'config.json') as config_json:
            config = json.load(config_json)
        self.YT_API = config["Youtube_api_token2"]
        self.TOKEN = config["Bot_token"]
        self.cmd_prefix = config["Command_prefix"]
        self.embed_color_msg = int(config["Embed_color_message"], 16)
        self.vabzeum_channel_id = int(config["vabzeum_channel"])
        self.vab_guild_id = int(config["vab_guild_id"])

        #paramètres
        self.client = discord.Client()
        self.yt_srch = yt_search.build(self.YT_API)
        self.youtube_list_regexp = youtube_list_regexp = "^(https?\:\/\/)?(www\.)?(youtube|youtu\.be)\.com\/watch\?v\=.+\&list\="
        self.youtube_regexp = youtube_regexp = "^(https?\:\/\/)?(www\.)?(youtube|youtu\.be)\.com\/watch\?v\="
        self.youtube_video_link = "http://www.youtube.com/watch?v="

        #musique
        self.musics_queue = []
        self.guild_list = []
        self.guild_nb = -1
        self.current_song = []

        #autre
        self.voice_client = None

    def on_command(self, guild, ctx = None):
        self.guild_nb = self.get_guild_nb(self.guild_list, guild)
        self.current_song = self.guild_list[self.guild_nb]["current_song"]
        self.musics_queue = self.guild_list[self.guild_nb]["musics_queue"]
        if ctx:
            if self.voice_client:
                self.last_voice_client = self.voice_client
            self.voice_client = ctx.guild.voice_client
            self.author_id = ctx.message.author.id
            self.author = ctx.message.author
            self.author_tag = ctx.message.author.mention
            self.message = ctx.message
            if ctx.message.author.voice:
                self.author_voice_channel = self.author.voice.channel
            else:
                self.author_voice_channel = None

    def set_voice_client(self, connection):
        self.voice_client = connection

    def adjust_ptr(self):
        self.current_song = self.guild_list[self.guild_nb]["current_song"]
        self.musics_queue = self.guild_list[self.guild_nb]["musics_queue"]


    def get_guild_nb(self, guild_list, guild):
        guild_name = str(guild)

        for elem in guild_list:
            if elem["guild_name"] == guild_name:
                return guild_list.index(elem)
    
        guild_list.append({"guild_name" : guild_name, "current_song" : None, "musics_queue" : []})
        for elem in guild_list:
            if elem["guild_name"] == guild_name:
                return guild_list.index(elem)
    
        print("ERREUR: probleme d'ajour du serveur dans guild_list")
        return False


    def play_song(self, song):
        #, before_options= "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(song.stream_url, **ffmpeg_options), volume = 0.1)
        
        def next(_):
            title = "Musique suivante"
            if len(self.guild_list[self.guild_nb]["musics_queue"]) > 0:
                new_song = self.guild_list[self.guild_nb]["musics_queue"][0]
                if new_song.error == False:
                    del self.guild_list[self.guild_nb]["musics_queue"][0]
                    if self.voice_client:
                        self.play_song(new_song)
                        self.guild_list[self.guild_nb]["current_song"] = new_song
                        ans = "**" + new_song.title + "**  [:arrow_upper_right:](" + new_song.url + ")"
                        asyncio.run_coroutine_threadsafe(send_embed_message(self, title = title, description = ans), self.client.loop)
                    else:
                        self.guild_list[self.guild_nb]["current_song"] = []
                        self.guild_list[self.guild_nb]["musics_queue"] = []
                else:
                    ans = "Erreur de lecture sur la musique suivante"
                    asyncio.run_coroutine_threadsafe(send_embed_message(self, title = title, description = ans), self.client.loop)
        try:
            self.voice_client.play(source, after = next)
        except Exception as e:
            print("le client n'est pas connecté")
        self.guild_list[self.guild_nb]["current_song"] = song
        self.adjust_ptr()
    

    def empty_queue(self, min = None, max = None, muted = False):
        title = "Nettoyage file d'attente"

        if len(self.guild_list[self.guild_nb]["musics_queue"]) == 0:
                ans = "La file d'attente est vide"
        elif (min and min.isdigit() and int(min) >= 1) and not max:
            nb = int(min)
            if len(self.guild_list[self.guild_nb]["musics_queue"]) >= nb:
                ans = "La musique n° " + str(nb) + ": **" + self.guild_list[self.guild_nb]["musics_queue"][nb - 1].title + "** a bien été supprimée"
                del self.guild_list[self.guild_nb]["musics_queue"][nb - 1]
        elif (min and min.isdigit() and int(min) >= 1) and (max and max.isdigit() and int(max) >= int(min)):
            min = int(min) - 1
            max = int(max) - 1
            i = 0
            ans = str(max - min) + (" musiques ont été retirées" if max < min else " musique a été retirée") + " de la liste de lecture"
            while max > min:
                del self.guild_list[self.guild_nb]["musics_queue"][max]
                max -= 1
        elif min == "all":
            ans = "La file a été vidée"
            self.guild_list[self.guild_nb]["musics_queue"] = []
        else:
            title = title + ": Erreur"
            ans = "** " + self.cmd_prefix + "clear all** pour vider la file\n** " + self.cmd_prefix + "clear [n° dans la liste]** pour supprimer la musique concernée\n**" + self.cmd_prefix + "clear [n° min] [n° max]** pour supprimer les musiques comprises dans l'intervalle"
        if not muted:
            asyncio.run_coroutine_threadsafe(send_embed_message(self, title = title, description = ans), self.client.loop)
        self.adjust_ptr()


    def author_is_connected(self):
        if self.author.voice == None:
            return False
        return True


    def check_url(self, url = None):
        check = 1
        if url == None:
            check = 0
        elif re.search("^https://www.youtube.com/", url.strip()) == None:
            check = 0
        # print(f"url checkée = [" + "None" if url == None else url + "]")
        if check == 1:
            # print("check url renvoie true")
            return True
        else:
            # print("check url renvoie false")
            return False
    

    def print_guild_list(self):
        print("====== lecture de guild_list ======")
        k = 0
        for guild in self.guild_list:
            current_song = guild["current_song"]
            musics_queue = guild["musics_queue"]
            print("\n     ------ SERVEUR " + str(k) + " ------")
            print("         guild_name: " + guild["guild_name"])
            if guild["current_song"]:
                print("         current_song: " + current_song.title + "\n              object_type: " + str(type(current_song)) + "\n              stream_url:" + str(current_song.stream_url) + "\n              url:" + current_song.url)
            else:
                print("         current_song: None")
            print("\n         musics_queue: ")
            i = 1
            for queue_list in musics_queue:
                print("\n         " + str(i) + ": " + queue_list.title + "\n              object_type: " + str(type(queue_list)) + "\n              stream_url:" + str(queue_list.stream_url) + "\n              url:" + queue_list.url)
                i += 1
            k += 1
        print("\n====== fin lecture de guild_list ======")


    def get_url_from_youtube(self, to_search = None, sMax = 10, sType = ["video"]):
        if to_search:
            to_search_result = self.yt_srch.search(to_search, sMax = sMax, sType = sType)
            video_id = str(to_search_result.videoId)
            if video_id == "[None]":
                ans = "Désolé " + self.author.mention + ", mais il y a un problème avec la recherche **" + to_search + "**"
                return None
            url = self.youtube_video_link + str(to_search_result.videoId).split("\'")[1]
            return url
        else:
            return None

    def is_youtube_list(self, url):
        if re.search(self.youtube_list_regexp, url.strip()):
            return True
        else:
            return False


    def load_list(self, url):
        priority = True
        previous_len_guild_list = len(self.musics_queue)
        yt_list = ytdl.extract_info(url, download = False)
        print(yt_list)
        i = 0
        k = 0

        if self.voice_client and self.voice_client.is_playing():
            priority = False

        for video in yt_list["entries"]:
            song = Song(video = video)
            if song.error == False and song.title and song.url and song.stream_url:
                if i == 0 and (not self.voice_client or (self.voice_client and not self.voice_client.is_playing())):
                    self.guild_list[self.guild_nb]["current_song"] = song
                else:
                    self.guild_list[self.guild_nb]["musics_queue"].append(song)
                i += 1
            else:
                print("la musique " + str(k) + " a eu un problème")
            k += 1
        len_guild_list = len(self.musics_queue)
        asyncio.run_coroutine_threadsafe(send_embed_message(self, description = str(len_guild_list - previous_len_guild_list) + " " + ("musiques ajoutées" if (len_guild_list - previous_len_guild_list) > 1 else "musique ajoutée") + " à la file"), self.client.loop)
        self.adjust_ptr()
        return priority


    def push_song(self, url, message = None):
        song = Song(url.split("&")[0])
        self.musics_queue.append(song)
        if not message:
            ans = "Ajout à la liste de lecture: **" + song.title + "  [:arrow_upper_right:](" + song.url + ")**"
        else:
            ans = message
        asyncio.run_coroutine_threadsafe(send_embed_message(self, description = ans), self.client.loop)
        self.adjust_ptr()


    def play(self, url, message = None):
        song = Song(url.split("&")[0])
        if song.error == False:
            self.play_song(song)
            if not message:
                ans = "Lecture de **" + song.title + "  [:arrow_upper_right:](" + song.url + ")**"
            else:
                ans = message
        else:
            ans = "Erreur de lecture sur la musique"
        asyncio.run_coroutine_threadsafe(send_embed_message(self, description = ans), self.client.loop)

    def get_queue(self, cmd = None, min = None, max = None):
        ans_list = []
        ans = ""
        len_guild_list = len(self.musics_queue)
        # if min and not max:
        #     max = len_guild_list

        if self.voice_client and self.voice_client.is_playing():
            if cmd and cmd == "extended":
                ans += ("En cours: " + self.current_song.title + ")\n\n")
            else:
                ans += ("En cours: **" + self.current_song.title + "**  [:arrow_upper_right:](" + self.current_song.url + ")\n\n")
        if len(self.musics_queue) == 0:
            ans += "\nLa file d'attente est vide"
            ans_list.append(ans)
            return ans_list
        
        i = 0
        while i < len(self.musics_queue):
            # if not min or (i >= min - 1 and i < max):
            if cmd and cmd == "extended":
                ans += (str(i + 1) + ": " + self.musics_queue[i].title + "\n")
            else:
                ans += (str(i + 1) + ":    **" + self.musics_queue[i].title + "**  [:arrow_upper_right:](" + self.musics_queue[i].url + ")\n")
            # if ((not min and i == 4) or (min and i == (min - 1 + 4))) and not cmd:
            #     ans += "**....**\n**..**\nPour voir la file d'attente complète, tape ** " + self.cmd_prefix + "queue all**"
            #     break
            if len(ans) > 1700:
                ans_list.append(ans)
                ans = ""
                # ans += "**....**\n**..**\nLa file d'attente est trop grande, tape ** " + self.cmd_prefix + "queue extended**"
            if cmd and cmd == "extended" and len(ans) > 1950:
                ans_list.append(ans)
                ans = ""
                # ans += ".\n.\nLa file est trop grande"
            i += 1
        ans_list.append(ans)
        return ans_list

    def send_queue(self, min = None, max = None, max2 = None):
        title = "File d'attente"
        cmd = None
        min_nb = None
        max_nb = None

        # print("\nchemin -->")
        if min:
            # print("if min")
            if min.isdigit():
                # print("if min is digit")
                min_nb = int(min)
                if max and max.isdigit():
                    # print("if max and max is digit")
                    max_nb = int(max)
            elif min == "all" or min == "extended":
                # print("elif min = all ou extended")
                cmd = min
                if max and max.isdigit():
                    # print("if max and max is digit")
                    min_nb = int(max)
                    if max2 and max2.isdigit():
                        # print("if max2 and max2 is digit")
                        max_nb = int(max2)
        else:
            # print("aucun des 3")
            ans_list = self.get_queue()
        # print("\ncmd = " + (cmd if cmd else "None"))
        # print("min_nb = " + (str(min_nb) if min_nb else "None"))
        # print("max_nb = " + (str(max_nb) if max_nb else "None"))
        # print("-----\n")
        if min_nb and max_nb:
            if max_nb < min_nb:
                max_nb = None
        ans_list = self.get_queue(cmd, min_nb, max_nb)

        i = 0
        # print("passage: longueur de liste = " + str(len(ans_list)))
        footer_separator = " - - - - - - - - - - - - - - - - - - - - - - - - - - - - - "
        footer = None
        while i < len(ans_list):
            # print("avant le if")
            if cmd == "all" or (min_nb and min_nb == i - 1) or (not min_nb and i == 0):
                # print("dans le if")
                if cmd == "all" and i > 0:
                    title = None
                if len(ans_list) > 1:
                    footer = footer_separator + "Page " + str(i + 1) + " sur " + str(len(ans_list)) + footer_separator
                asyncio.run_coroutine_threadsafe(send_embed_message(self, title = title, description = ans_list[i], footer = footer), self.client.loop)
            # print("après le if")
            i += 1