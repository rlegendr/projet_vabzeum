import sqlite3
import os
import shutil

from os import getcwd

UPLOADS_DIR = getcwd() + "/../static/uploads/"

for filename in os.listdir(UPLOADS_DIR):
    file_path = os.path.join(UPLOADS_DIR, filename)
    try:
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)
    except Exception as e:
        print('Failed to delete %s. Reason: %s' % (file_path, e))


# os.remove( + match["screen_name"])
connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())


cur = connection.cursor()

# cur.execute("INSERT INTO account (id_discord_user_datas, password, admin) VALUES (?, ?, ?)",
#             (1, 'mdp', 1)
#             )

i = 0
while i < 5:
    cur.execute("INSERT INTO vabzeum_match_datas (used_nickname, ally_1, ally_2, ally_3, ally_4, ally_5, nb_ally, nb_vab, nb_ennemy, diff, entity, side, bonus_mult, bonus_mult_name, screen_name)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                ('Kromy', 'Kromy', 'Fina', 'Qyo', 'Shrimp', 'San', 3, 3, 5, 2, "Percepteur", "Attaque", 2, "JOKER", "None")
                )
    # cur.execute("INSERT INTO vabzeum_match_datas (used_nickname, ally_1, ally_2, ally_3, ally_4, ally_5, nb_ally, nb_vab, nb_ennemy, diff, entity, side, bonus_mult, bonus_mult_name, id_match, screen_name)"
    #             " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    #             ('Kromy', 'Kromy', 'Fina', 'Qyo', 'Shrimp', 'San', 3, 5, 2, 1, "percepteur", "Attaque", 2, "JOKER", 110, "None")
    #             )
    # cur.execute("INSERT INTO vabzeum_match_datas (used_nickname, ally_1, ally_2, ally_3, ally_4, ally_5, nb_ally, nb_vab, nb_ennemy, diff, entity, side, bonus_mult, bonus_mult_name, id_match, screen_name)"
    #             " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    #             ('Kromy', 'Kromy', 'Fina', 'Qyo', 'Shrimp', 'San', 3, 5, 2, 1, "percepteur", "Attaque", 2, "JOKER", 1, "None")
    #             )
    # cur.execute("INSERT INTO vabzeum_match_datas (used_nickname, ally_1, ally_2, ally_3, ally_4, ally_5, nb_ally, nb_vab, nb_ennemy, diff, entity, side, bonus_mult, bonus_mult_name, id_match, screen_name)"
    #             " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
    #             ('Kromy', 'Kromy', 'Fina', 'Qyo', 'Shrimp', 'San', 3, 5, 2, 1, "percepteur", "Attaque", 2, "JOKER", 12, "None")
    #             )
    print(i)
    i += 1

cur.execute("INSERT INTO bonus_mult (name, mult, effective) VALUES (?, ?, ?)", ("Aucun", 1, 0))
cur.execute("INSERT INTO bonus_mult (name, mult, effective) VALUES (?, ?, ?)", ("JOKER", 2, 0))
cur.execute("INSERT INTO bonus_mult (name, mult, effective) VALUES (?, ?, ?)", ("LEVIA", 3, 0))

cur.execute("INSERT INTO discord_user_datas (nickname, tag, password, effective, admin) VALUES (?, ?, ?, ?, ?)", ('Kromy', '<@!161174796078415872>', "3dbb218f858e988fed5c2c27ccbac7dc", 1, 1))
cur.execute("INSERT INTO discord_user_datas (nickname, tag, password, effective, admin) VALUES (?, ?, ?, ?, ?)", ('San', '<@!183348713391915008>', "mdpSan", 1, 0))
cur.execute("INSERT INTO discord_user_datas (nickname, tag, password, effective, admin) VALUES (?, ?, ?, ?, ?)", ('Shrimp', '<@!352522952232927234>', "mdpShrimp", 1, 1))
cur.execute("INSERT INTO discord_user_datas (nickname, tag, password, effective, admin) VALUES (?, ?, ?, ?, ?)", ('Qyo', '<@!369777535925616640>', "mdpQyo", 1, 1))
cur.execute("INSERT INTO discord_user_datas (nickname, tag, password, effective, admin) VALUES (?, ?, ?, ?, ?)", ('Fina', '<@!399989615919890453>', "mdpFina", 1, 1))
cur.execute("INSERT INTO discord_user_datas (nickname, tag, password, effective, admin) VALUES (?, ?, ?, ?, ?)", ('Stenchou', '<@!447447950084276235>', "mdpStenchou", 1, 1))
cur.execute("INSERT INTO discord_user_datas (nickname, tag, password, effective, admin) VALUES (?, ?, ?, ?, ?)", ('Kromy2', '<@!727781966908227594>', "mdpKromy2", 1, 1))

cur.execute("INSERT INTO score_index (side, diff, points) VALUES (?, ?, ?)", ("Attaque", -4, 2))
cur.execute("INSERT INTO score_index (side, diff, points) VALUES (?, ?, ?)", ("Attaque", -3, 4))
cur.execute("INSERT INTO score_index (side, diff, points) VALUES (?, ?, ?)", ("Attaque", -2, 6))
cur.execute("INSERT INTO score_index (side, diff, points) VALUES (?, ?, ?)", ("Attaque", -1, 8))
cur.execute("INSERT INTO score_index (side, diff, points) VALUES (?, ?, ?)", ("Attaque", 0, 10))
cur.execute("INSERT INTO score_index (side, diff, points) VALUES (?, ?, ?)", ("Attaque", 1, 15))
cur.execute("INSERT INTO score_index (side, diff, points) VALUES (?, ?, ?)", ("Attaque", 2, 25))
cur.execute("INSERT INTO score_index (side, diff, points) VALUES (?, ?, ?)", ("Attaque", 3, 40))
cur.execute("INSERT INTO score_index (side, diff, points) VALUES (?, ?, ?)", ("Attaque", 4, 100))
cur.execute("INSERT INTO score_index (side, diff, points) VALUES (?, ?, ?)", ("Défense", -4, 2))
cur.execute("INSERT INTO score_index (side, diff, points) VALUES (?, ?, ?)", ("Défense", -3, 4))
cur.execute("INSERT INTO score_index (side, diff, points) VALUES (?, ?, ?)", ("Défense", -2, 6))
cur.execute("INSERT INTO score_index (side, diff, points) VALUES (?, ?, ?)", ("Défense", -1, 8))
cur.execute("INSERT INTO score_index (side, diff, points) VALUES (?, ?, ?)", ("Défense", 0, 20))
cur.execute("INSERT INTO score_index (side, diff, points) VALUES (?, ?, ?)", ("Défense", 1, 30))
cur.execute("INSERT INTO score_index (side, diff, points) VALUES (?, ?, ?)", ("Défense", 2, 50))
cur.execute("INSERT INTO score_index (side, diff, points) VALUES (?, ?, ?)", ("Défense", 3, 80))
cur.execute("INSERT INTO score_index (side, diff, points) VALUES (?, ?, ?)", ("Défense", 4, 200))


cur.execute("INSERT INTO bot_state (pid, lifeline) VALUES (?, ?)", (1, '2021-01-14 00:00:00'))


connection.commit()
connection.close()