from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user 
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Club, Player
from functools import wraps
import datetime
from markupsafe import escape
import subprocess
import logging
from utils import *
from kfutils import *
from jfilters import *
from pzkconfig import licencje
from payu import get_redirect_uri


# logger file
logging.basicConfig(filename="admin.log", 
                    level=logging.WARNING, #DEBUG,
                    format="%(asctime)s:%(levelname)s:%(message)s")

# Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'kendo'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Use SQLite database (you can change this to another database URL)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Flask-Login configuration
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Check if the current user is logged in and is an admin
        if current_user:
            logging.debug(f'{current_user.surname} called {f.__name__}')
        else:
            logging.debug(f'visitor called {f.__name__}')

        if current_user.is_authenticated and current_user.admin:
            return f(*args, **kwargs)
        else:
            # Redirect to a different page or show an error message
            # You can also abort with a 403 Forbidden status code
            flash('You do not have permission to access this page (403).', 'error')
            return redirect(url_for('home'))
    return wrapper


# Register the filter with Jinja2
app.jinja_env.filters['is_older_than_one_year'] = is_older_than_one_year
app.jinja_env.filters['is_younger_than_one_year'] = is_younger_than_one_year
app.jinja_env.filters['dan'] = dan
app.jinja_env.filters['shogo'] = shogo
app.jinja_env.filters['ymd'] = ymd


# Routes
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/log')
@login_required
@admin_required
def see_log():
    with open('admin.log') as f:
        x = f.readlines()
    return render_template('log.html', x=x)

@app.route('/update_app')
@login_required
@admin_required
def update_app():
    command = subprocess.run(["git", "pull"], 
                                  stdout=subprocess.PIPE, 
                                  text=True)
    if command.returncode:
        flash(f"The exit code was: {command.stdout}", 'error')
    else:
        flash(f"The exit code was: {command.stdout}", 'success')

    command = subprocess.run(["touch", "tmp/restart.txt"], 
                                  stdout=subprocess.PIPE, 
                                  text=True)
    if command.returncode:
        flash(f"The exit code was: {command.stdout}", 'error')
    else:
        flash(f"The exit code was: {command.stdout}", 'success')

    return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = escape(request.form['username'])
        password = escape(request.form['password'])

        user = User.query.filter_by(username=username).first()
        # print(user)

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')

            if not user.rodo:
                return redirect(url_for('rodo'))

            if not user.coc:
                return redirect(url_for('coc'))

            return redirect(url_for('profile'))
        else:
            flash('Login failed. Check your username and password.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful!', 'success')
    return redirect(url_for('home'))


@app.route('/rodo', methods=['GET', 'POST'])
@login_required
def rodo():
    if request.method == 'POST':
        rodo = escape(request.form['rodo'])
        
        if rodo == 'true':
            current_user.rodo = datetime.datetime.now()
            db.session.commit()
            flash('Dziękujemy za zgodę na RODO.', 'success')
            return redirect(url_for('coc'))
        else:
            flash('Nie można założyć konta, wymagana zgoda na RODO.', 'error')
            return redirect(url_for('logout'))

    return render_template('rodo.html', agreement=current_user.rodo)


@app.route('/coc', methods=['GET', 'POST'])
@login_required
def coc():
    if request.method == 'POST':
        coc = escape(request.form['coc'])
        
        if coc == 'true':
            current_user.coc = datetime.datetime.now()
            db.session.commit()
            flash('Dziękujemy za zgodę na Kodeks.', 'success')
            return redirect(url_for('profile', username=current_user.username))
        else:
            flash('Nie można założyć konta, wymagana zgoda na Kodeks Postępowania PZK.', 'error')
            return redirect(url_for('logout'))

    return render_template('coc.html', agreement=current_user.coc)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = escape(request.form['username'])
        email = escape(request.form['email'])
        password = escape(request.form['password'])
        key = escape(request.form['secretkey'])
        rodo = datetime.datetime.now() if escape(request.form['rodo']) == 'true' else False

        if not rodo:
            flash('Nie można założyć konta, wymagana zgoda na RODO.', 'error')
            return redirect(url_for('logout'))

        # TODO:
        #   - check id password and confirm_password agree

        if User.query.filter_by(username=username).first():
            # Check if the username already exists
            flash('Użytkownik istnieje już w bazie.', 'error')
        else:
            club = Club.query.filter_by(club_key=key).first()
            if club:
                # If code OK
                # Create a new user
                new_user = User(
                    username=username,
                    password=generate_password_hash(password),
                    email=email,
                    rodo=rodo,
                    clubID=club.id,
                )
                db.session.add(new_user)
                db.session.commit()
                # u = User.query.filter_by(username=username).first()
                # u.playeriD = f'PZK.{u.id:05}'
                # db.session.commit()

                flash('Rejestracja przebiegła poprawnie! Możesz się zalogować.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Zły kod klubu.', 'error')

    return render_template('register.html')


@app.route('/profile')
@login_required
def profile():
    player = Player.query.filter_by(userID=current_user.id).first()
    club = Club.query.filter_by(id=current_user.clubID).first()
    return render_template('profile.html', user=current_user, player=player, club=club)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # current_user.username = request.form['username']
        current_user.name = escape(request.form['name'])
        current_user.surname = escape(request.form['surname'])
        current_user.email = escape(request.form['email'])
        current_user.phone = escape(request.form['phone'])
        db.session.commit()
        flash('Nowe dane zapisane.', 'success')
        return redirect(url_for('profile'))

    return render_template('edit_profile.html', user=current_user)


@app.route('/clubs')
def clubs():
    # Query all clubs from the database
    clubs = Club.query.all()
    return render_template('clubs.html', clubs=clubs)


@app.route('/users')
def users():
    # Query all clubs from the database
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/instructors')
def instructors():
    # Query all players from the database
    clubs = Club.query.all()
    players = Player.query.all()
    return render_template('instructors.html', players=players, user=current_user, clubs=clubs)


@app.route('/add_instructor')
@login_required
@admin_required
def add_instructor():
    # Query all players from the database
    clubs = Club.query.all()
    players = Player.query.all()
    return render_template('add_instructor.html', players=players, user=current_user, clubs=clubs)


@app.route('/edit_instructor/<int:id>', methods=['POST'])
@login_required
@admin_required
def edit_instructor(id):
    player = Player.query.get_or_404(id)
    if request.method == 'POST':
        if player.instructor == None:
            player.instructor = '000'

        new_kendo = escape(request.form.get('newKendo'))
        if new_kendo == None:
            new_kendo = player.instructor[0]
        
        new_iaido = escape(request.form.get('newIaido'))
        if new_iaido == None:
            new_iaido = player.instructor[1]
        
        new_jodo = escape(request.form.get('newJodo'))
        if new_jodo == None:
            new_jodo = player.instructor[2]
        
        player.instructor = str(new_kendo) + str(new_iaido) + str(new_jodo)
        db.session.commit()
        return redirect(url_for('instructors'))
    return "404"  #redirect(url_for('players'))  #render_template('players.html', items=Player.query.all())



@app.route('/players')
def players():
    # Query all players from the database
    clubs = Club.query.all()
    players = Player.query.all()
    return render_template('players.html', players=players, user=current_user, clubs=clubs)


################################################
################# licencje #####################

@app.route('/payment', methods=['POST'])
@login_required
def payment():
    if request.method == 'POST':
        info = f'_{current_user.name}_{current_user.surname}_'
        hajs = 50
        kendo = request.form.get('licencjaKendo')
        if kendo != None:
            hajs += 150
            info += 'k'
        iaido = request.form.get('licencjaIaido')
        if iaido != None:
            hajs += 150
            info += 'i'
        jodo = request.form.get('licencjaJodo')
        if jodo != None:
            hajs += 150
            info += 'j'

        # here place PayU order
        payment_uri = get_redirect_uri(amount=hajs, player_info=info)
        return render_template(
            'checkout.html', 
            user=current_user, 
            amount=hajs,
            info=info,
            uri=payment_uri
            )  
        
    return redirect(url_for('profile'))

@app.route('/licences') #, methods=['GET', 'POST'])
@login_required
def licences():
    player = Player.query.filter_by(userID=current_user.id).first()
    club = Club.query.filter_by(id=current_user.clubID).first()
    return render_template('user_licence.html', user=current_user, player=player, club=club)


@app.route('/pay_off_licence')
@login_required
def pay_off_licence():
    player = Player.query.filter_by(userID=current_user.id).first()
    return render_template('pay_off_licence.html', player=player, user=current_user, licencje=licencje)

################################################


@app.route('/edit_player/<int:id>', methods=['POST'])
@login_required
@admin_required
def edit_player(id):
    player = Player.query.get_or_404(id)
    if request.method == 'POST':
        player.kendo = grade_from_form(request.form.get('newKendo'))
        player.iaido = grade_from_form(request.form.get('newIaido'))
        player.jodo = grade_from_form(request.form.get('newJodo'))

        player.kendolicence = set_licence_date(request.form.get('kendolicence'))
        player.iaidolicence = set_licence_date(request.form.get('iaidolicence'))
        player.jodolicence = set_licence_date(request.form.get('jodolicence'))
        player.licence = kf_licence(player)

        player.kendoshogo = set_shogo(player, request.form.get('kendoshogo'), 'kendo')
        player.iaidoshogo = set_shogo(player, request.form.get('iaidoshogo'), 'iaido')
        player.jodoshogo = set_shogo(player, request.form.get('jodoshogo'), 'jodo')
            
        db.session.commit()
        return redirect(url_for('players'))
    return "404"  #redirect(url_for('players'))  #render_template('players.html', items=Player.query.all())




@app.route('/edit_uplayer', methods=['GET', 'POST'])
@login_required
def edit_uplayer():
    if not current_user.name or not current_user.surname:
        flash('Najpierw dodaj imię i nazwisko profilu głównym', 'error')
        return redirect(url_for('edit_profile'))

    player = Player.query.filter_by(userID=current_user.id).first()
    club = Club.query.filter_by(id=current_user.clubID).first()

    if request.method == 'POST':
        name = ''
        if isinstance(current_user.name, str):
            name += current_user.name
        if isinstance(current_user.surname, str):
            name += " " + current_user.surname
        
        kendograde = int(escape(request.form.get('kendo')))
        kendoshogo = int(escape(request.form.get('kendoshogo')))
        iaidograde = int(escape(request.form.get('iaido')))
        iaidoshogo = int(escape(request.form.get('iaidoshogo')))
        jodograde = int(escape(request.form.get('jodo')))
        jodoshogo = int(escape(request.form.get('jodoshogo')))

        address = str(escape(request.form.get('address'))).strip()
        pesel = str(escape(request.form.get('pesel'))).strip()
        if not is_valid_pesel(pesel):
            flash('Niepoprawny PESEL.', 'error')
            return redirect(url_for('edit_uplayer'))

        if player:
            player.name = name

            player.kendo = kendograde
            player.kendoshogo = kendoshogo
            player.iaido = iaidograde
            player.iaidoshogo = iaidoshogo
            player.jodo = jodograde
            player.jodoshogo = jodoshogo

            if address:
                player.address = address
            
            if pesel:
                player.pesel = pesel

        else:
            new_player = Player(
                userID=current_user.id,
                name=name,
                pesel=pesel if pesel else '',
                address=address if address else '',
                kendo=kendograde if kendograde else 0,
                kendoshogo=kendoshogo,
                iaido=iaidograde if iaidograde else 0,
                iaidoshogo=iaidoshogo,
                jodo=jodograde if jodograde else 0,
                jodoshogo=jodoshogo,
                club=club.id,
                )
            db.session.add(new_player)
            db.session.commit()
            p = Player.query.filter_by(userID=current_user.id).first()
            p.playeriD = get_playeriD(p.id)

        db.session.commit()
        return redirect(url_for('profile'))
    
    return render_template('edit_uplayer.html', user=current_user, player=player, club=club)


if __name__ == '__main__':
    # app.run(debug=True)
    app.run()