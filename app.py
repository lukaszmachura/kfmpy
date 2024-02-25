from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user 
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Club, Player
from functools import wraps
import datetime
from utils import is_valid_pesel, get_playeriD


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
    def decorated_function(*args, **kwargs):
        # Check if the current user is logged in and is an admin
        if current_user.is_authenticated and current_user.admin:
            return f(*args, **kwargs)
        else:
            # Redirect to a different page or show an error message
            # You can also abort with a 403 Forbidden status code
            flash('You do not have permission to access this page (403).', 'error')
            return redirect(url_for('home'))
    return decorated_function


def is_older_than_one_year(date):
    if date == None:
        return False
    
    current_date = datetime.datetime.now()
    one_year_ago = current_date - datetime.timedelta(days=365)
    
    if date < one_year_ago:
        return True
    else:
        return False
    
def is_younger_than_one_year(date):
    if date == None:
        return False
    return not is_older_than_one_year(date)

def dan(g):
    if g == None:
        return ''
    g = int(g)
    if g > 0:
        return f'{g} dan'
    else:
        return f'{-g} kyu'

def shogo(g):
    g = int(g)
    if g == 1:
        return 'Renshi'
    elif g == 2:
        return 'Kyoshi'
    elif g == 3:
        return 'Hanshi'
    return ''

# Register the filter with Jinja2
app.jinja_env.filters['is_older_than_one_year'] = is_older_than_one_year
app.jinja_env.filters['is_younger_than_one_year'] = is_younger_than_one_year
app.jinja_env.filters['dan'] = dan
app.jinja_env.filters['shogo'] = shogo

# Routes
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

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
        rodo = request.form['rodo']
        
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
        coc = request.form['coc']
        
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
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        key = request.form['secretkey']
        rodo = datetime.datetime.now() if request.form['rodo'] == 'true' else False

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
        current_user.name = request.form['name']
        current_user.surname = request.form['surname']
        current_user.email = request.form['email']
        current_user.phone = request.form['phone']
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

        new_kendo = request.form.get('newKendo')
        if new_kendo == None:
            new_kendo = player.instructor[0]
        
        new_iaido = request.form.get('newIaido')
        if new_iaido == None:
            new_iaido = player.instructor[1]
        
        new_jodo = request.form.get('newJodo')
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


@app.route('/template')
def template():
    items = User.query.all()
    return render_template('template.html', items=items)


@app.route('/edit_player/<int:id>', methods=['POST'])
@login_required
@admin_required
def edit_player(id):
    player = Player.query.get_or_404(id)
    if request.method == 'POST':
        new_kendo = request.form.get('newKendo')
        if new_kendo:
            player.kendo = new_kendo

        new_iaido = request.form.get('newIaido')
        if new_iaido:
            player.iaido = new_iaido
        
        new_jodo = request.form.get('newJodo')
        if new_jodo:
            player.jodo = new_jodo

        kendoactive = request.form.get('kendoactive')
        iaidoactive = request.form.get('iaidoactive')
        jodoactive = request.form.get('jodoactive')
        licence = 0
        if kendoactive:
            licence += int(kendoactive)
        if iaidoactive:
            licence += int(iaidoactive)
        if jodoactive:
            licence += int(jodoactive)
        player.licence = licence

        kendolicence = request.form.get('kendolicence')
        if kendolicence:
            player.kendolicence = datetime.datetime.strptime(kendolicence, '%Y-%m-%d')
        
        iaidolicence = request.form.get('iaidolicence')
        if iaidolicence:
            player.iaidolicence = datetime.datetime.strptime(iaidolicence, '%Y-%m-%d')

        jodolicence = request.form.get('jodolicence')
        if jodolicence:
            player.jodolicence = datetime.datetime.strptime(jodolicence, '%Y-%m-%d')

        kendoshogo = request.form.get('kendoshogo')
        if kendoshogo:
            player.kendoshogo = int(kendoshogo)
            
        iaidoshogo = request.form.get('iaidoshogo')
        if iaidoshogo:
            player.iaidoshogo = int(iaidoshogo)
        
        jodoshogo = request.form.get('jodoshogo')
        if jodoshogo:
            player.jodoshogo = int(jodoshogo)

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
        
        new_kendo = request.form.get('kendo')
        kendoshogo = int(request.form.get('kendoshogo'))
        new_iaido = request.form.get('iaido')
        iaidoshogo = int(request.form.get('iaidoshogo'))
        new_jodo = request.form.get('jodo')
        jodoshogo = int(request.form.get('jodoshogo'))

        address = request.form.get('address')
        pesel = request.form.get('pesel')
        if not is_valid_pesel(pesel):
            flash('Niepoprawny PESEL.', 'error')
            return redirect(url_for('edit_uplayer'))

        if player:
            player.name = name

            if new_kendo:
                player.kendo = new_kendo
            if kendoshogo:
                player.kendoshogo = kendoshogo

            if new_iaido:
                player.iaido = new_iaido
            if iaidoshogo:
                player.iaidoshogo = iaidoshogo
            
            if new_jodo:
                player.jodo = new_jodo
            if jodoshogo:
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
                kendo=new_kendo if new_kendo else '',
                kendoshogo=kendoshogo,
                iaido=new_iaido if new_iaido else '',
                iaidoshogo=iaidoshogo,
                jodo=new_jodo if new_jodo else '',
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
    app.run(debug=True)