from minitwit import dba
from flask_login import UserMixin


class discord_user_datas(UserMixin, dba.Model):
    id = dba.Column(dba.Integer, primary_key=True)
    nickname = dba.Column(dba.String(30), unique=True)
    tag = dba.Column(dba.String(50), unique=True)
    password = dba.Column(dba.String(100), unique=True)
    effective = dba.Column(dba.Integer, unique=True)
    admin = dba.Column(dba.Integer, unique=True)
    created = dba.Column(dba.DateTime, unique=True)


class vabzeum_match_datas(dba.Model):
    id = dba.Column(dba.Integer, primary_key=True)
    used_nickname = dba.Column(dba.String(30), unique=True)
    ally_1 = dba.Column(dba.String(30), unique=True)
    ally_2 = dba.Column(dba.String(30), unique=True)
    ally_3 = dba.Column(dba.String(30), unique=True)
    ally_4 = dba.Column(dba.String(30), unique=True)
    ally_5 = dba.Column(dba.String(30), unique=True)
    nb_ally = dba.Column(dba.Integer, unique=True)
    nb_vab = dba.Column(dba.Integer, unique=True)
    nb_ennemy = dba.Column(dba.Integer, unique=True)
    diff = dba.Column(dba.Integer, unique=True)
    entity = dba.Column(dba.String(30), unique=True)
    side = dba.Column(dba.String(30), unique=True)
    bonus_mult = dba.Column(dba.Integer, unique=True)
    bonus_mult_name = dba.Column(dba.String(30), unique=True)
    screen_name = dba.Column(dba.String(30), unique=True)
    bot_checker = dba.Column(dba.Integer, unique=True)
    admin_validator = dba.Column(dba.Integer, unique=True)
    score = dba.Column(dba.Integer, unique=True)
    commentary = dba.Column(dba.String, unique=True)
    created = dba.Column(dba.DateTime, unique=True)

    def get_ally(self, nb):
        all_ally = [self.ally_1, self.ally_2, self.ally_3, self.ally_4, self.ally_5]
        return all_ally[nb]


class bonus_mult(dba.Model):
    id = dba.Column(dba.Integer, primary_key=True)
    name = dba.Column(dba.String(30), unique=True)
    mult = dba.Column(dba.Integer, unique=True)
    effective = dba.Column(dba.Integer, unique=True)


class score_index(dba.Model):
    id = dba.Column(dba.Integer, primary_key=True)
    side = dba.Column(dba.String(30), unique=True)
    diff = dba.Column(dba.Integer, unique=True)
    points = dba.Column(dba.Integer, unique=True)


class bot_state(dba.Model):
    id = dba.Column(dba.Integer, primary_key=True)
    pid = dba.Column(dba.Integer, unique=True)
    lifeline = dba.Column(dba.DateTime, unique=True)


