import sqlite3

from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, FileField, StringField, PasswordField, widgets, BooleanField, DateTimeField
from flask_wtf.file import FileRequired, FileAllowed
from wtforms.validators import DataRequired


ATK_DEF = [('Attaque', 'Attaque'), ('Défense', 'Défense')]
NB_ALLY = [('nb_ally_1', '1'), ('nb_ally_2', '2'), ('nb_ally_3', '3'), ('nb_ally_4', '4'), ('nb_ally_5', '5')]
NB_VAB = [('nb_vab_1', '1'), ('nb_vab_2', '2'), ('nb_vab_3', '3'), ('nb_vab_4', '4'), ('nb_vab_5', '5')]
NB_ENNEMY = [('nb_ennemy_1', '1'), ('nb_ennemy_2', '2'), ('nb_ennemy_3', '3'), ('nb_ennemy_4', '4'), ('nb_ennemy_5', '5')]
ENTITY = [('Percepteur', 'Percepteur'), ('Prisme', 'Prisme')]


def get_db_connection():
    conn = sqlite3.connect('./db/database.db')
    conn.row_factory = sqlite3.Row
    return conn


class RegisterMatch(FlaskForm):
    atk_def = SelectField('Attaque / Défense: ', choices = ATK_DEF, validators=[DataRequired()])
    nb_ally = SelectField('Alliers: ', choices = NB_ALLY, validators=[DataRequired()])
    nb_vab = SelectField('VàB: ', choices = NB_VAB, validators=[DataRequired()])
    nb_ennemy = SelectField('Ennemis: ', choices = NB_ENNEMY, validators=[DataRequired()])
    entity = SelectField('Percepteur / Prisme: ', choices = ENTITY, validators=[DataRequired()])
    ally_1 = SelectField('Allier 1: ', validate_choice=False)
    ally_2 = SelectField('Allier 2: ', validate_choice=False)
    ally_3 = SelectField('Allier 3: ', validate_choice=False)
    ally_4 = SelectField('Allier 4: ', validate_choice=False)
    ally_5 = SelectField('Allier 5: ', validate_choice=False)
    bonus_mult = SelectField('Code Promo: ', validate_choice=False)
    screen = FileField("ScreenShot du match: ", validators=[FileRequired(), FileAllowed(['jpg', 'png'], 'Images only!')])
    commentary = StringField("Commentaire: ")
    validate_button = SubmitField("Valider")


class LoginForm(FlaskForm):
    username = StringField("Surnom discord", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    submit = SubmitField("Connexion")


class ModifyUser(FlaskForm):
    username = StringField("Surnom discord")
    password = PasswordField("Mot de passe")
    tag = StringField("Tag discord")
    effective = BooleanField("Compte effectif")
    admin = BooleanField("Administrateur")
    submit_modify_user = SubmitField("Modifier")


class CreateUser(FlaskForm):
    username = StringField("Surnom discord", validators=[DataRequired()])
    password = PasswordField("Mot de passe", validators=[DataRequired()])
    tag = StringField("Tag discord", validators=[DataRequired()])
    effective = BooleanField("Compte effectif")
    admin = BooleanField("Administrateur")
    submit_create_user = SubmitField("Enregistrer")


class ModifyMatch(FlaskForm):
    id = StringField("id du match:")
    used_nickname = StringField("Enregistreur: ")
    ally_1 = SelectField('1: ', validate_choice=False)
    ally_2 = SelectField('2: ', validate_choice=False)
    ally_3 = SelectField('3: ', validate_choice=False)
    ally_4 = SelectField('4: ', validate_choice=False)
    ally_5 = SelectField('5: ', validate_choice=False)
    nb_ally = SelectField('Nombre d\'alliers: ', choices=NB_ALLY, validators=[DataRequired()])
    nb_vab = SelectField('Nombre de VàB: ', choices=NB_VAB, validators=[DataRequired()])
    nb_ennemy = SelectField('Nombre d\'ennemis: ', choices=NB_ENNEMY, validators=[DataRequired()])
    entity = SelectField('Percepteur / Prisme: ', choices = ENTITY, validators=[DataRequired()])
    side = SelectField('Attaque / Défense: ', choices = ATK_DEF, validators=[DataRequired()])
    bonus_mult = StringField("Valeur du bonus: ")
    bonus_mult_name = StringField("Code du bonus: ")
    bot_checker = BooleanField("Traité par le bot (si décoché, le bot republiera le match)")
    admin_validator = BooleanField("Validation du match (à cocher si le match est valide)")
    score = StringField("Score: ")
    commentary = StringField("Commentaire: ")
    submit_modify_match = SubmitField("Enregistrer")

    def set_dynamic_fields(self, members, code_promo):
        all_players = [(elem.id, elem.nickname) for elem in members]
        all_players = sorted(all_players, key=lambda x: x[1])
        list_players = list(all_players)
        list_players.insert(0, (None, ""))
        self.ally_1.choices = list_players
        self.ally_2.choices = list_players
        self.ally_3.choices = list_players
        self.ally_4.choices = list_players
        self.ally_5.choices = list_players


class ModifyCode(FlaskForm):
    id = StringField("id du code:")
    name = StringField("Nom: ")
    mult = StringField("Multiplicateur:")
    effective = BooleanField("Effectif:")
    submit_modify_code = SubmitField("Enregistrer")
    submit_delete_code = SubmitField("Supprimer")


class CreateCode(FlaskForm):
    id = StringField("id du code:")
    name = StringField("Nom: ", validators=([DataRequired()]))
    mult = StringField("Multiplicateur:", validators=([DataRequired()]))
    effective = BooleanField("Effectif:")
    submit_create_code = SubmitField("Créer")


class ModifyScale(FlaskForm):
    id = StringField("id: ")
    diff = StringField("Diff: ")
    side = StringField("Atk/Déf: ")
    points = StringField("Points: ", validators=([DataRequired()]))
    submit_modify_scale = SubmitField("Modifier")


# class SearchMatch(FlaskForm):
#     start_date = DateTimeField("Date de début", validators=([DataRequired()]))
#     end_date = DateTimeField("Date de fin", validators=([DataRequired()]))
#     submit_search_match = SubmitField("Rechercher")


class GenScore(FlaskForm):
    start_date = StringField("Date de début", validators=([DataRequired()]))
    end_date = StringField("Date de fin", validators=([DataRequired()]))
    submit_gen_score = SubmitField("Générer")
    # submit_create_csv = SubmitField("Créer un CSV")

