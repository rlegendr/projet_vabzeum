import sys
import re
import discord
import sqlite3
import os
import json

from os import getcwd
from pathlib import Path


class Mypath:
    def __init__(self):
        try:
            with open('paths.json', 'r') as paths_config:
                self.paths = json.load(paths_config)
        except FileNotFoundError:
            with open('../paths.json', 'r') as paths_config:
                self.paths = json.load(paths_config)
        self.app = self.paths["app"]
        self.bot = self.paths["bot"]
        self.static = self.paths["static"]
        self.db = self.paths["db"]
        self.uploads = self.paths["uploads"]
        self.title = self.paths["title"]


def get_db_connection():
    conn = sqlite3.connect(Mypath().db + 'database.db')
    conn.row_factory = sqlite3.Row
    return conn


async def send_message(hub = None, description = None, message = None):
    if description:
        if hub:
            await hub.message.channel.send(description)
        elif message:
            await message.channel.send(description)


async def send_embed_message(hub = None, title = None, description = None, type = 'rich', url = None, color = None, message = None, footer = None, img_link = None, img_name = None):

    embed_msg = discord.Embed(title = title, description = description, type = type, color = color if color else 2706252, footer = footer)

    if footer:
        embed_msg.set_footer(text = footer)
    file = None
    if hub:
        if img_link:
            file = discord.File(img_link, filename=img_link)
            embed_msg.set_image(url="attachment://" + img_name)
        await hub.message.channel.send(embed=embed_msg, file=file)
    elif message:
        if img_link:
            file = discord.File(img_link, filename=img_link)
            embed_msg.set_image(url="attachment://" + img_name)
        await message.channel.send(embed=embed_msg, file=file)
    else:
        print("ERREUR ENVOIE MESSAGE")


async def send_match(match, message, db, connection):
    title = f"Match n° **{match['id']}**"
    msg = f"Combat en **{match['side']}** contre un **{match['entity']}**\n" \
          f"**{match['nb_ally']}** allier(s) dont **{match['nb_vab']}** VàB, contre **{match['nb_ennemy']}** ennemis\n" \
          f"Liste des VàB:\n"
    msg += f"**{match['ally_1']}**"
    if match['ally_2'] and match['ally_2'] != "None":
        msg += f", **{match['ally_2']}**"
    if match['ally_3'] and match['ally_3'] != "None":
        msg += f", **{match['ally_3']}**"
    if match['ally_4'] and match['ally_4'] != "None":
        msg += f", **{match['ally_4']}**"
    if match['ally_5'] and match['ally_5'] != "None":
        msg += f", **{match['ally_5']}**"
    if match['bonus_mult'] > 1:
        msg += f".\nMultiplicateur: **x{match['bonus_mult']}**, code: **{match['bonus_mult_name']}**.\n"
    else:
        msg += ".\n**Aucun** multiplicateur.\n"
    msg += f"Compte utilisé pour l'inscription: **{match['used_nickname']}**"
    if match["commentary"]:
        msg += f"\nCommentaire:\n```{match['commentary']}```"
    if match["screen_name"] == "None":
        img_name = None
        img_link = None
    else:
        img_name = match["screen_name"]
        img_link = Mypath().uploads + match["screen_name"]
    if img_link and not Path(img_link).exists():
        img_link = None
        img_name = None
    await send_embed_message(title=title, description=msg, message=message, img_link=img_link, img_name=img_name)
    db.execute(f"UPDATE vabzeum_match_datas SET bot_checker = 1 WHERE id = {match['id']}")
    connection.commit()


def is_admin(db, players, tag):
    for elem in players:
        if tag == elem["tag"] and elem["admin"] == 1:
            return True
    return False


async def print_db(hub, db):
    tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    cut = "   /   "
    nl = "\n"
    for tab in tables:
        if tab["name"] != "sqlite_sequence":
            table_name = db.execute(f"PRAGMA table_info({tab['name']});").fetchall()
            table = db.execute(f"SELECT * FROM {tab['name']}").fetchall()

            msg = ""
            mytable = []
            for elem in table_name:
                msg += elem["name"] + cut
                mytable.append(elem["name"])
            msg += nl
            for elem in table:
                for elem2 in mytable:
                    msg += str(elem[elem2]) + cut
                msg += nl
            await send_embed_message(hub, f"table {tab['name']}", msg)


class Message:
    def __init__(self, channel):
        self.channel = channel
