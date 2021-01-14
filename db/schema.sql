DROP TABLE IF EXISTS account;
DROP TABLE IF EXISTS vabzeum_datas;
DROP TABLE IF EXISTS vabzeum_match_datas;
DROP TABLE IF EXISTS bonus_mult;
DROP TABLE IF EXISTS discord_user_datas;
DROP TABLE IF EXISTS score_index;
DROP TABLE IF EXISTS bot_state;


-- CREATE TABLE account (
--     id INTEGER PRIMARY KEY AUTOINCREMENT,
--     id_discord_user_datas INTEGER,
--     password TEXT NOT NULL,
--     admin INTEGER,
--     created INTEGER DEFAULT CURRENT_TIMESTAMP
-- );

CREATE TABLE bot_state (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pid INTEGER DEFAULT 0,
    lifeline DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vabzeum_match_datas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    used_nickname TEXT NOT NULL,
    ally_1 TEXT NOT NULL,
    ally_2 TEXT NULL,
    ally_3 TEXT NULL,
    ally_4 TEXT NULL,
    ally_5 TEXT NULL,
    nb_ally INTEGER,
    nb_vab INTEGER,
    nb_ennemy INTEGER,
    diff INTEGER,
    entity TEXT NOT NULL,
    side TEXT NOT NULL,
    bonus_mult INTEGER DEFAULT 1,
    bonus_mult_name TEXT NULL,
    screen_name TEXT NOT NULL,
    bot_checker INTEGER DEFAULT 0,
    admin_validator INTEGER DEFAULT 0,
    score INTEGER DEFAULT 0,
    commentary TEXT DEFAULT NULL,
    created DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bonus_mult (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    mult INTEGER DEFAULT 1,
    effective INTEGER DEFAULT 1
);

CREATE TABLE discord_user_datas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nickname TEXT NOT NULL,
    tag TEXT NOT NULL,
    password TEXT NOT NULL,
    effective INTEGER,
    admin INTEGER,
    created DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE score_index (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    side   TEXT NOT NULL,
    diff   INTEGER,
    points INTEGER
)
