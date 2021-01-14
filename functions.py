import sqlite3
import os
import sys
import re
import hashlib

from sqlite3 import OperationalError, ProgrammingError
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from os import getcwd
from datetime import datetime
from minitwit import Mypath


def logs(message):
    file = open("logs.txt", "a")
    file.write(message)
    file.close()


def get_db_connection():
    conn = sqlite3.connect('./db/database.db')
    conn.row_factory = sqlite3.Row
    return conn


def get_post(post_id):
    conn = get_db_connection()
    post = conn.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    conn.close()
    if post is None:
        abort(404)
    return post


def set_dynamic_fields(db, form):
    players = db.execute("SELECT `id`, `nickname` FROM `discord_user_datas`").fetchall()
    code_promo = db.execute("SELECT `id`, `name`, `mult` FROM `bonus_mult` WHERE `effective` = 1").fetchall()
    all_players = [(elem["id"], elem["nickname"]) for elem in players]
    all_players = sorted(all_players, key=lambda x: x[1])
    list_players = list(all_players)
    list_players.insert(0, (None, ""))
    form.ally_1.choices = list_players
    form.ally_2.choices = list_players
    form.ally_3.choices = list_players
    form.ally_4.choices = list_players
    form.ally_5.choices = list_players
    form.bonus_mult.choices = [(elem6["id"], elem6["name"] + " | x" + str(elem6["mult"])) for elem6 in code_promo]


def get_nickname(id_player):
    if not id_player or id_player == "None":
        return 'None'
    id_player = int(id_player)
    connection = get_db_connection()
    db = connection.cursor()
    id_player = db.execute('SELECT nickname FROM discord_user_datas WHERE id = ' + str(id_player))
    for elem in id_player:
        nickname = elem['nickname']
    db.close()
    connection.close()
    return nickname


def fill_match(form, current_user, bonus_mult, score_index):
    connection = get_db_connection()
    db = connection.cursor()

    match = dict()
    match["used_nickname"] = current_user.nickname
    match["ally_1"] = get_nickname(form.ally_1.data)
    match["ally_2"] = get_nickname(form.ally_2.data)
    match["ally_3"] = get_nickname(form.ally_3.data)
    match["ally_4"] = get_nickname(form.ally_4.data)
    match["ally_5"] = get_nickname(form.ally_5.data)
    match["nb_ally"] = int(form.nb_ally.data.split('_')[2])
    match["nb_vab"] = int(form.nb_vab.data.split('_')[2])
    match["nb_ennemy"] = int(form.nb_ennemy.data.split('_')[2])
    match["diff"] = match["nb_ennemy"] - match["nb_ally"]
    match["entity"] = form.entity.data
    match["side"] = form.atk_def.data
    match["bonus_mult"] = form.bonus_mult.data
    match["bonus_mult_name"] = bonus_mult.query.filter_by(id=form.bonus_mult.data).first().name
    match["id"] = get_match_id()

    f = form.screen.data
    filename = secure_filename(f.filename)
    match["screen_name"] = str(match["id"]) + filename[len(filename) - 4:]
    f.save(Mypath().uploads + match["screen_name"])

    match["score"] = score_index.query.filter_by(side=match["side"], diff=match["diff"]).first().points
    if form.commentary.data:
        match["commentary"] = form.commentary.data
    else:
        match["commentary"] = None

    db.close()
    connection.close()
    return match


def get_match_id():
    connection = get_db_connection()
    db = connection.cursor()
    nb_line = (db.execute("SELECT COUNT(*) FROM vabzeum_match_datas").fetchall())[0]["count(*)"]
    # print(str(nb_line) + " de type " + str(type(nb_line)))
    if nb_line == 0:
        return 1
    id = (db.execute("SELECT MAX(id) FROM vabzeum_match_datas;").fetchall())[0]["max(id)"]
    return int(id) + 1


def insert_match(match, db=None, connection=None):
    # print(match)
    try:
        db.execute(
            'INSERT INTO  vabzeum_match_datas' +
            '(used_nickname, ally_1, ally_2, ally_3, ally_4, ally_5, nb_ally, nb_vab, nb_ennemy, diff, entity, side, bonus_mult, bonus_mult_name, screen_name, score, commentary) ' +
            'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            (match["used_nickname"],
             match["ally_1"],
             match["ally_2"],
             match["ally_3"],
             match["ally_4"],
             match["ally_5"],
             match["nb_ally"],
             match["nb_vab"],
             match["nb_ennemy"],
             match["diff"],
             match["entity"],
             match["side"],
             match["bonus_mult"],
             match["bonus_mult_name"],
             match["screen_name"],
             match["score"],
             match["commentary"]
             ))
        connection.commit()
        return "OK"
    except (
    sqlite3.NotSupportedError, sqlite3.IntegrityError, sqlite3.OperationalError, sqlite3.ProgrammingError) as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}\n"
        message = template.format(type(ex).__name__, ex.args)
        os.remove(Mypath().uploads + match["screen_name"])
        logs(message)
        return None


def vabhash(to_hash):
    ret = Mypath().title.split('_')[0] + to_hash + Mypath().title.split('_')[1] + Mypath().title.split('_')[2]
    ret = hashlib.md5(ret.encode()).hexdigest()
    return ret


def update_member(id, member, form, dba, discord_user_datas):
    if form.username.data:
        double = discord_user_datas.query.filter_by(nickname=form.username.data)
        for elem in double:
            return "Ce pseudo est déjà utilisé"
        member.nickname = form.username.data
    if form.password.data:
        member.password = vabhash(form.password.data)
    if form.tag.data:
        double = discord_user_datas.query.filter_by(tag=form.tag.data)
        for elem in double:
            return f"Ce tag est déjà utilisé par {elem.nickname}"
        if not re.search("^<@![0-9]{18}>$", form.tag.data):
            return "Mauvais format pour le tag"
    member.effective = 1 if form.effective.data else 0
    member.admin = 1 if form.admin.data else 0
    dba.session.commit()
    return None


def register_member(form, dba, discord_user_datas):
    if not form.username.data or not form.password.data or not form.tag.data:
        return "Le formulaire est incomplet"
    double = discord_user_datas.query.filter_by(nickname=form.username.data)
    for elem in double:
        return "Ce pseudo est déjà utilisé"
    double = discord_user_datas.query.filter_by(tag=form.tag.data)
    for elem in double:
        return f"Ce tag est déjà utilisé par {elem.nickname}"
    if not re.search("^<@![0-9]{18}>$", form.tag.data):
        return "Mauvais format pour le tag"
    new_row = discord_user_datas(nickname=form.username.data,
                                 tag=form.tag.data,
                                 password=vabhash(form.password.data),
                                 effective=form.effective.data,
                                 admin=form.admin.data,
                                 created=datetime.now().replace(microsecond=0))
    dba.session.add(new_row)
    dba.session.commit()
    return None


def update_match(match, form, dba, discord_user_datas, score_index):
    match.ally_1 = "None" if (
                form.ally_1.data == "None" or not form.ally_1.data) else discord_user_datas.query.filter_by(
        id=form.ally_1.data).first().nickname
    match.ally_2 = "None" if (
                form.ally_2.data == "None" or not form.ally_2.data) else discord_user_datas.query.filter_by(
        id=form.ally_2.data).first().nickname
    match.ally_3 = "None" if (
                form.ally_3.data == "None" or not form.ally_3.data) else discord_user_datas.query.filter_by(
        id=form.ally_3.data).first().nickname
    match.ally_4 = "None" if (
                form.ally_4.data == "None" or not form.ally_4.data) else discord_user_datas.query.filter_by(
        id=form.ally_4.data).first().nickname
    match.ally_5 = "None" if (
                form.ally_5.data == "None" or not form.ally_5.data) else discord_user_datas.query.filter_by(
        id=form.ally_5.data).first().nickname
    match.nb_ally = form.nb_ally.data.split('_')[2]
    if form.nb_vab.data:
        match.nb_vab = form.nb_vab.data.split('_')[2]
    if form.nb_ennemy.data:
        match.nb_ennemy = form.nb_ennemy.data.split('_')[2]
    if form.side.data:
        match.side = form.side.data
    if form.entity.data:
        match.entity = form.entity.data
    if form.bonus_mult.data:
        match.bonus_mult = form.bonus_mult.data
    if form.bonus_mult_name.data:
        match.bonus_mult_name = form.bonus_mult_name.data
    match.bot_checker = 1 if form.bot_checker.data == 1 else 0
    match.admin_validator = 1 if form.admin_validator.data == 1 else 0
    match.diff = int(match.nb_ennemy) - int(match.nb_ally)
    match.score = score_index.query.filter_by(side=match.side, diff=match.diff).first().points
    if form.admin_validator.data == 1:
        if match.screen_name != "None":
            try:
                with open(Mypath().uploads + match.screen_name):
                    pass
                os.remove(Mypath().uploads + match.screen_name)
            except IOError:
                pass
            match.screen_name = "None"
    if form.commentary.data:
        match.commentary = form.commentary.data
    else:
        match.commentary = None
    dba.session.commit()


def calcul_points(matchs):
    scores = {}
    for match in matchs:
        if match.ally_1 not in scores and match.ally_1 != "None":
            scores[match.ally_1] = {"Attaque": 0, "Défense": 0}
        if match.ally_2 not in scores and match.ally_2 != "None":
            scores[match.ally_2] = {"Attaque": 0, "Défense": 0}
        if match.ally_3 not in scores and match.ally_3 != "None":
            scores[match.ally_3] = {"Attaque": 0, "Défense": 0}
        if match.ally_4 not in scores and match.ally_4 != "None":
            scores[match.ally_4] = {"Attaque": 0, "Défense": 0}
        if match.ally_5 not in scores and match.ally_5 != "None":
            scores[match.ally_5] = {"Attaque": 0, "Défense": 0}
        if match.ally_1 != "None":
            scores[match.ally_1][match.side] += (match.score * int(match.bonus_mult))
        if match.ally_2 != "None":
            scores[match.ally_2][match.side] += (match.score * int(match.bonus_mult))
        if match.ally_3 != "None":
            scores[match.ally_3][match.side] += (match.score * int(match.bonus_mult))
        if match.ally_4 != "None":
            scores[match.ally_4][match.side] += (match.score * int(match.bonus_mult))
        if match.ally_5 != "None":
            scores[match.ally_5][match.side] += (match.score * int(match.bonus_mult))
    scores_list = []
    for elem in scores:
        scores_list.append([elem, scores[elem]['Attaque'], scores[elem]['Défense']])
    return scores_list


def sort_score(scores):
    i = 0
    tmp = []
    while i + 1 < len(scores):
        if (scores[i][1] + scores[i][2]) < (scores[i + 1][1] + scores[i + 1][2]):
            tmp = scores[i + 1]
            scores[i + 1] = scores[i]
            scores[i] = tmp
            i = 0
        else:
            i += 1
    i = 0
    # for elem in scores:
    #     print(elem)
    while i < len(scores):
        scores[i].append(i + 1)
        i += 1
    return scores


def check_pid(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def is_bot_alive(bot_state):
    bot_stats = bot_state.query.filter_by(id=1).first()
    # lifeline = datetime.strptime(datetimebot_stats.lifeline, '%Y-%m-%d %H:%M:%S')
    lifeline = bot_stats.lifeline.timestamp()
    now = datetime.now().timestamp()
    alive_time = now - lifeline
    if alive_time > 6:
        return False
    if not check_pid(bot_stats.pid):
        return False
    return True