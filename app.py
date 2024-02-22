from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user 
#, UserMixin
# from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Club, Player
from functools import wraps

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
            flash('You do not have permission to access this page.', 'error')
            return redirect(url_for('home'))
        # "You do not have permission to access this page.", 403
    return decorated_function


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



@app.route('/coc', methods=['GET', 'POST'])
@login_required
def coc():
    if request.method == 'POST':
        coc = request.form['coc']
        
        if coc == 'true':
            current_user.coc = True
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
        password = request.form['password']
        key = request.form['secretkey']
        rodo = True if request.form['rodo'] == 'true' else False

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
                    rodo=rodo,
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
    if player:
        club = Club.query.filter_by(id=player.club).first()
    else:
        club = None
    return render_template('profile.html', user=current_user, player=player, club=club)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        # Update user profile information based on the form submission
        current_user.username = request.form['username']
        current_user.kendo = request.form['kendo']
        current_user.iaido = request.form['iaido']
        current_user.jodo = request.form['jodo']
        db.session.commit()
        flash('Nowe dane zapisane.', 'success')
        return redirect(url_for('profile', username=current_user.username))

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
    
        db.session.commit()
        return redirect(url_for('players'))
    return "404"  #redirect(url_for('players'))  #render_template('players.html', items=Player.query.all())


@app.route('/edit_instructor/<int:id>', methods=['POST'])
@login_required
def edit_instructor(id):
    player = Player.query.get_or_404(id)
    if request.method == 'POST':
        new_kendo = request.form.get('newKendo')
        new_iaido = request.form.get('newIaido')       
        new_jodo = request.form.get('newJodo')
        player.instructor = str(new_kendo) + str(new_iaido) + str(new_jodo)
        db.session.commit()
        return redirect(url_for('instructors'))
    return "404"  #redirect(url_for('players'))  #render_template('players.html', items=Player.query.all())



if __name__ == '__main__':
    app.run(debug=True)