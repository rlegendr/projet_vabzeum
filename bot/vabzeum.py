import discord
import sys
import sqlalchemy
import datetime

from datetime import datetime
from discord.ext import commands, tasks
from random import choice
from tools import *
from hub import *
import sqlite3
from os import getcwd
from sqlalchemy import create_engine


global hub
global id_vab_guild
global id_channel_vab

# id_vab_guild = 619291342207582208
# id_channel_vab = 700252769793081365

hub = VabCommand()
client = discord.Client()
status = ["massacrer JOKER", "bichonner ses VaB", "taper un cré à tord", "compter les points du vabzeum"]
client = commands.Bot(command_prefix = hub.cmd_prefix)
config_vabzeum = "vabzeum_config.json"
register_error_msg = hub.cmd_prefix + "register Ton_Surnom Ton_Tag\n\n**exemple: **" + hub.cmd_prefix + "register Kromy @Krominey#3957"
engine = create_engine(f'sqlite:///{Mypath().db}database.db', echo=True)

# LANCEMENT DU BOT
@client.event
async def on_ready():
    loop_status.start()
    loop_check_match.start()
    loop_is_alive.start()
    connection = get_db_connection()
    db = connection.cursor()
    query = f"UPDATE bot_state SET pid = {os.getpid()}, lifeline = '{datetime.now()}' WHERE id = 1"
    db.execute(query)
    print('Le bot est connecté sous: {0.user}'.format(client) + '\n --- V A B ---')
    connection.commit()
    db.close()
    connection.close()


@tasks.loop(seconds=10)
async def loop_status():
    await client.change_presence(activity=discord.Game(choice(status)))


@tasks.loop(seconds=5)
async def loop_is_alive():
    connection = get_db_connection()
    db = connection.cursor()
    query = f"UPDATE bot_state SET pid = {os.getpid()}, lifeline = '{datetime.now()}' WHERE id = 1"
    db.execute(query)
    connection.commit()
    db.close()


@tasks.loop(seconds=5)
async def loop_check_match():
    connection = get_db_connection()
    db = connection.cursor()
    unchecked_matches = db.execute("SELECT * FROM vabzeum_match_datas WHERE bot_checker == 0").fetchall()
    if not unchecked_matches:
        db.close()
        connection.close()
        return
    guilds_list = client.guilds
    for guild in guilds_list:
        if guild.id == hub.vab_guild_id:
            for channel in guild.channels:
                if channel.id == hub.vabzeum_channel_id:
                    for elem in unchecked_matches:
                        await send_match(elem, Message(channel), db, connection)
    db.close()
    connection.close()


# COMMANDE PING
@client.command(name='ping', help='renvoie la latence avec le bot')
async def ping(ctx):
    hub.on_command(ctx.guild, ctx)
    await send_embed_message(hub, description = f'**Pong!** {round(client.latency * 1000)}ms')


@client.command(name="register", help="Enregistre un nouveau joueur dans le vabzeum")
async def register(ctx, nickname = None, player_tag = None, put_admin = None):
    hub.on_command(ctx.guild, ctx)
    connection = get_db_connection()
    db = connection.cursor()
    all_players = db.execute('SELECT * FROM discord_user_datas').fetchall()
    admin = is_admin(db, all_players, hub.author_tag)

    if nickname == None or player_tag == None:
        await send_embed_message(hub, "VabZeum - Inscription - Erreur", register_error_msg)
        return
    if player_tag != hub.author_tag and not admin:
        await send_embed_message(hub, "VabZeum - Inscription - Erreur", "Tu ne peux pas inscrire une autre personne que toi")
        return

    for player in all_players:
        if nickname == player["nickname"]:
            await send_embed_message(hub, "VabZeum - Inscription - Erreur", "Le surnom **" + nickname + "** est déjà utilisé")
            return
        if player_tag == player["tag"]:
            await send_embed_message(hub, "VabZeum - Inscription", player_tag + " est déjà inscrit  sous le surnom: **" + player["nickname"] + "**")
            return
    if put_admin == "admin" and admin:
        put_admin = 1
    else:
        put_admin = 0

    # print(f"rqt envoyee \nINSERT INTO discord_user_datas (nickname, tag, admin) VALUES (?, ?, ?)', ({nickname}, {player_tag}, {put_admin})")
    db.execute('INSERT INTO discord_user_datas (nickname, tag, admin) VALUES (?, ?, ?)', (nickname, player_tag, put_admin))
    await send_embed_message(hub, "VabZeum - Inscription", "Tu es maintenant inscrit " + player_tag + " sous le surnom: **" + nickname + "**")
    connection.commit()
    db.close()
    connection.close()



@client.command(name="players", help="liste les joueurs enregistrés dans le vabzeum")
async def players(ctx):
    hub.on_command(ctx.guild, ctx)
    connection = get_db_connection()
    db = connection.cursor()
    players = db.execute('SELECT * FROM discord_user_datas').fetchall()
    res = ""
    for player in players:
        if player["tag"] == hub.author_tag:
            res += "**" + player["nickname"] + "**"
        else:
            res += player["nickname"]
        res += f"  --  {player['admin']}\n"
    await send_embed_message(hub, "VabZeum - Inscrits", res)
    db.close()
    connection.close()


@client.command(name="db", help="")
async def print_database(ctx):
    hub.on_command(ctx.guild, ctx)
    connection = get_db_connection()
    db = connection.cursor()
    players = db.execute('SELECT * FROM discord_user_datas').fetchall()
    for player in players:
        if hub.author_tag == player["tag"] and player["admin"] != 1:
            await send_embed_message(hub, "Impression base", "Tu n'as pas les droits pour utiliser cette commande")
            db.close()
            connection.close()
            return
    await print_db(hub, db)
    db.close()
    connection.close()


@client.command(name="getchannels", help="")
async def getchannels(ctx):
    guilds_list = client.guilds
    for guild in guilds_list:
        if guild.id == hub.vab_guild_id:
            for channel in guild.channels:
                print(f'"{channel}" : "{channel.id}",')
    return


@client.command(name="getmembers", help="")
async def getmembers(ctx):
    hub.on_command(ctx.guild, ctx)
    # print(f"nombre de membres: {len(hub.message.guild.members)}")
    # return
    guilds_list = client.guilds
    for guild in guilds_list:
        if guild.id == hub.vab_guild_id:
            print(f"nombre de membres: {len(guild.members)}")
            for member in guild.members:
                print(f'"{member}" : "{member.id}",')
                for role in member.roles:
                    print(f'\t"{role}"')
    return


@client.command(name="score", help="")
async def score(ctx):
    hub.on_command(ctx.guild, ctx)
    connection = get_db_connection()



# /////////////////////////////////////////////////////////////////////////////

@client.command(name="bite", help="Seule une personne est capable d'utiliser cette commande")
async def bite(ctx):
    hub.on_command(ctx.guild, ctx)
    if hub.author_id == 352522952232927234:
        await send_embed_message(hub, "MESSAGE IMPORTANT", "Le Grand SHRIMP a dit bite !")
    else:
        await send_message(hub, "c ki " + hub.author_tag + "?")


@client.command(name="stenjoke", help="Une bonne blague de sten :D")
async def stenjoke(ctx, nb = None):
    hub.on_command(ctx.guild, ctx)
    with open(Mypath().bot + 'stenjoke.json') as stenjoke_json:
        try:
            stenjoke = json.load(stenjoke_json)
        except json.decoder.JSONDecodeError:
            await send_embed_message(hub, title=f"Les blagues à la Sten sont en pause pour quelques secondes :D")
            return
    nb_jokes = len(stenjoke["jokes"]) - 1
    if nb:
        try:
            nb = int(nb)
            if nb > nb_jokes or nb < 0:
                await send_embed_message(hub, title=f"Les blagues à la Sten ({nb} (wtf?!?)/{nb_jokes})", description="Désolé je la connais pas celle là :poop:")
                return
        except ValueError:
            nb = choice(range(nb_jokes))
    else:
        nb = choice(range(nb_jokes))
    await send_embed_message(hub, title=f"Les blagues à la Sten ({nb}/{nb_jokes})", description=stenjoke["jokes"][nb])

# BOUCLE D'EXECUTION
client.run(hub.TOKEN)