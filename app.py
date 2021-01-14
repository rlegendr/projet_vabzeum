import sys
import calendar
import time
import json

from os import getcwd

cwd = getcwd() + '/'
paths = {
    "app": cwd,
    "bot": f"{cwd}bot/",
    "static": f"{cwd}static/",
    "db": f"{cwd}db/",
    "uploads": f"{cwd}static/uploads/",
    "title": "Vague_à_bons"
}

with open('paths.json', 'w') as json_paths:
    json.dump(paths, json_paths)


class Mypath:
    def __init__(self):
        with open('paths.json', 'r') as paths_config:
            self.paths = json.load(paths_config)
        self.app = self.paths["app"]
        self.bot = self.paths["bot"]
        self.static = self.paths["static"]
        self.db = self.paths["db"]
        self.uploads = self.paths["uploads"]
        self.title = self.paths["title"]


from is_safe_url import is_safe_url
from flask import Flask, render_template, session, flash, request, redirect, url_for
from forms import RegisterMatch, LoginForm, ModifyUser, CreateUser, CreateCode, ModifyCode, ModifyMatch, ModifyScale, GenScore
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from functions import *


sys.path.insert(0, getcwd() + "./")

app = Flask(__name__)
app.config["SECRET_KEY"] = "clef pour csrf"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{Mypath().db}database.db"
dba = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

from db import vabzeum_match_datas, discord_user_datas, bonus_mult, score_index, bot_state


@login_manager.user_loader
def load_user(user_id):
    return discord_user_datas.query.get(int(user_id))


def is_admin(f):
    @wraps(f)
    def decorated_fct(*args, **kwargs):
        if not current_user.admin:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_fct


@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')


@app.route('/')
def index():
    return render_template('common/index.html')

# CONNEXION /////


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = discord_user_datas.query.filter_by(nickname=form.username.data, password=vabhash(form.password.data)).first()
        if not user:
            flash('Erreur dans le surnom ou le mot de passe', "message_error")
            return redirect("/login")
        if user.effective == 0:
            flash('Ton compte a été suspendu', "message_error")
            return redirect("/login")
        login_user(user)
        flash(f'Tu es connecté sous le surnom: {current_user.nickname}')
        # next = request.args.get('next')
        # if not is_safe_url(next):
        #     return abort(400)
        return redirect('/')
    return render_template('common/login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Tu as bien été déconnecté')
    return redirect('/')


# VABZEUM //////

@app.route('/vabzeum')
def vabzeum():
    nb_all_match = dba.session.query(vabzeum_match_datas.id).count()
    nb_match_not_validated = dba.session.query(vabzeum_match_datas.id).filter(vabzeum_match_datas.admin_validator == 0).count()
    nb_match = 0
    year = datetime.now().year
    month = datetime.now().month
    last_day = calendar.monthrange(year, month)[1]
    start = datetime(year=int(year), month=int(month), day=int(1), hour=0, minute=0, second=0)
    end = datetime(year=int(year), month=int(month), day=int(last_day), hour=23, minute=59, second=59)
    matchs = vabzeum_match_datas.query.filter(
        vabzeum_match_datas.created.between(start, end) & vabzeum_match_datas.admin_validator == 1)
    for elem in matchs:
        nb_match += 1
    scores = calcul_points(matchs)
    scores = sort_score(scores)
    print(scores)
    return render_template('common/vabzeum_accueil.html', scores=scores, nb_match=nb_match, nb_all_match=nb_all_match, nb_match_not_validated=nb_match_not_validated)


@app.route('/vabzeum/register_match', methods=['GET', 'POST'])
@login_required
def register_match():
    connection = get_db_connection()
    db = connection.cursor()
    form = RegisterMatch()
    if form.validate_on_submit():
        match = fill_match(form, current_user, bonus_mult, score_index)
        if not insert_match(match, db, connection):
            flash("Il y a eu une erreur lors de l'enregistrement", "message_error")
        else:
            flash("Ton match a bien été enregistré :)")
        return redirect(url_for('redirect_register_match'))
    set_dynamic_fields(db, form)
    db.close()
    connection.close()
    return render_template('common/vabzeum_register_match.html', form=form)


@app.route('/vabzeum/register_match/insert')
@login_required
def redirect_register_match():
    return redirect(url_for('register_match'))


# ADMIN /////


@app.route('/admin')
@login_required
@is_admin
def admin():
    if is_bot_alive(bot_state):
        bot_status = "ok"
    else:
        bot_status = None
    return render_template('admin/admin.html', bot_status=bot_status)


@app.route('/admin/start_bot')
@login_required
@is_admin
def start_bot():
    if is_bot_alive(bot_state):
        flash('Le bot est déjà allumé', "message_bot")
        return redirect(url_for('admin'))
    os.system(f"python3 bot/vabzeum.py")
    return redirect(url_for('admin'))


@app.route('/admin/stop_bot')
@login_required
@is_admin
def stop_bot():
    if not is_bot_alive(bot_state):
        flash("Le bot est déjà arrêté", "message_bot")
    else:
        bot = bot_state.query.filter_by(id=1).first()
        os.system(f"kill -9 {bot.pid}")
    return redirect(url_for('admin'))


# @app.route('/admin/pid/', methods=['GET'])
# @login_required
# @is_admin
# def pid():
#     pid = int(request.args.get("pid"))
#     try:
#         os.kill(pid, 0)
#     except OSError:
#         return "pas bon"
#     else:
#         return "bon"



@app.route('/admin/members_list')
@login_required
@is_admin
def members_list():
    members = discord_user_datas.query.all()
    return render_template('admin/members_list.html', members=members)


@app.route('/admin/members_list/<int:id>/delete')
@login_required
@is_admin
def delete_member(id):
    member = discord_user_datas.query.filter_by(id=id).first().nickname
    discord_user_datas.query.filter_by(id=id).delete()
    dba.session.commit()
    flash(f"{member} a bien été supprimé")
    return redirect('/admin/members_list')


@app.route('/admin/members_list/<id>', methods=['GET', 'POST'])
@login_required
@is_admin
def modify_member(id):
    form = ModifyUser()
    member = discord_user_datas.query.filter_by(id = id).first()
    if not member:
        return redirect(url_for('members_list'))
    if form.validate_on_submit():
        if form.submit_modify_user.data:
            error = update_member(id, member, form, dba, discord_user_datas)
            if error:
                flash(error, "message_error")
                return redirect(url_for('modify_member', id=id))
            return redirect('/admin/members_list')
        if not member:
            return redirect('/admin/members_list')
    return render_template(f'admin/modify_member.html', form=form, member=member)


@app.route('/admin/create_member', methods=['GET', 'POST'])
@login_required
@is_admin
def create_member():
    form = CreateUser()
    if form.validate_on_submit():
        error = register_member(form, dba, discord_user_datas)
        if error:
            flash(error, "message_error")
        else:
            flash(f"Le membre {form.username.data} a bien été enregistré")
            return redirect(url_for('create_member'))
    return render_template(f'admin/create_member.html', form=form)


@app.route('/admin/matchs_list/', methods=['GET'])
@login_required
@is_admin
def matchs_list():
    id = request.args.get("search_id_match")
    if not id:
        # matchs = vabzeum_match_datas.query.all()
        matchs = vabzeum_match_datas.query.order_by(vabzeum_match_datas.id.desc()).limit(50)
        nb_match = dba.session.query(vabzeum_match_datas.id).count()
    else:
        matchs = vabzeum_match_datas.query.filter_by(id=id).all()
        nb_match = 1
    return render_template('admin/matchs_list.html', matchs=matchs, nb_match=nb_match)


@app.route('/admin/matchs_list/<int:id>/delete')
@login_required
@is_admin
def delete_match(id):
    vabzeum_match_datas.query.filter_by(id=id).delete()
    dba.session.commit()
    flash(f"Le match {id} a bien été supprimé")
    return redirect('/admin/matchs_list')


@app.route('/admin/matchs_list/<int:id>', methods=['GET', 'POST'])
@login_required
@is_admin
def modify_match(id):
    form = ModifyMatch()
    members = discord_user_datas.query.all()
    code_promo = bonus_mult.query.all()
    match = vabzeum_match_datas.query.filter_by(id = id).first()
    form.set_dynamic_fields(members, code_promo)
    members_id = {}
    for member in members:
        members_id[member.nickname] = member.id
    if form.validate_on_submit():
        match = vabzeum_match_datas.query.filter_by(id=id).first()
        update_match(match, form, dba, discord_user_datas, score_index)
        return redirect('/admin/matchs_list')
    if not match:
        return redirect('/admin/matchs_list')
    return render_template(f'admin/modify_match.html', form=form, match=match, members_id=members_id)



@app.route('/admin/codes_list')
@login_required
@is_admin
def codes_list():
    codes = bonus_mult.query.all()
    return render_template('admin/codes_list.html', codes=codes)


@app.route('/admin/codes_list/<int:id>', methods=['GET', 'POST'])
@login_required
@is_admin
def modify_code(id):
    form = ModifyCode()
    if form.validate_on_submit():
        if form.submit_modify_code.data:
            table = bonus_mult.query.filter_by(id=id).first()
            if form.name.data:
                if bonus_mult.query.filter_by(name=form.name.data).first():
                    flash("Le code existe déjà", "message_error")
                    return redirect(url_for('modify_code', id=id))
                table.name = form.name.data
            if form.mult.data:
                table.mult = form.mult.data
            table.effective = 1 if form.effective.data == 1 else 0
            dba.session.commit()
            flash("Le code à bien été modifié")
        if form.submit_delete_code.data:
            bonus_mult.query.filter_by(id=id).delete()
            dba.session.commit()
            flash("Le code à bien été supprimé")
        return redirect(url_for('codes_list'))
    code = bonus_mult.query.filter_by(id=id).first()
    if not code:
        return redirect('/admin/codes_list')
    return render_template('admin/modify_code.html', form=form, code=code)


@app.route('/admin/create_code', methods=['GET', 'POST'])
@login_required
@is_admin
def create_code():
    form = CreateCode()
    if form.validate_on_submit():
        if bonus_mult.query.filter_by(name=form.name.data).first():
            flash("Le code existe déjà", "message_error")
            return redirect(url_for('create_code'))
        new_row = bonus_mult(name = form.name.data,
                             mult = form.mult.data,
                             effective = form.effective.data,
                             created = datetime.now().replace(microsecond = 0))
        dba.session.add(new_row)
        dba.session.commit()
        # flash
        return redirect(url_for('codes_list'))
    return render_template('admin/create_code.html', form=form)


@app.route('/admin/manage_scale/')
@login_required
@is_admin
def manage_scale():
    atks = score_index.query.filter_by(side="Attaque").all()
    defs = score_index.query.filter_by(side="Défense").all()
    return render_template('admin/manage_scale.html', atks=atks, defs=defs)


@app.route('/admin/manage_scale/<int:id>', methods=['GET', 'POST'])
@login_required
@is_admin
def modify_scale(id):
    form = ModifyScale()
    if form.validate_on_submit():
        scale = score_index.query.filter_by(id=id).first()
        if form.points.data:
            scale.points = form.points.data
            dba.session.commit()
        return redirect(url_for("manage_scale"))
    scale = score_index.query.filter_by(id=id).first()
    if not scale:
        return redirect('/admin/manage_scale')
    return render_template("admin/modify_scale.html", form=form, scale=scale)


@app.route('/admin/generate_score', methods=['GET', 'POST'])
@login_required
@is_admin
def generate_score():
    form = GenScore()
    scores = None
    nb_match = 0
    display = None
    if form.validate_on_submit():
        start = form.start_date.data.split('-')
        end = form.end_date.data.split('-')
        try:
            start = datetime(year=int(start[0]), month=int(start[1]), day=int(start[2]), hour=0, minute=0, second=0)
            end = datetime(year=int(end[0]), month=int(end[1]), day=int(end[2]), hour=23, minute=59, second=59)
        except ValueError:
            flash("Erreur dans la date", "message_error")
            return redirect(url_for('generate_score'))
        matchs = vabzeum_match_datas.query.filter(vabzeum_match_datas.created.between(start, end) & vabzeum_match_datas.admin_validator == 1)
        for elem in matchs:
            nb_match += 1
        scores = calcul_points(matchs)
        scores = sort_score(scores)
        display = True
    return render_template("admin/generate_score.html", form=form, scores=scores, nb_match=nb_match, display=display)


