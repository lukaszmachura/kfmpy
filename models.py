from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

db = SQLAlchemy()

class User(db.Model, UserMixin):
    '''user table model'''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    parentID = db.Column(db.Integer)  # make this local reference
    clubID = db.Column(db.Integer)  # TODO make this club reference
    leader = db.Column(db.Boolean, default=False)

    email = db.Column(db.String(100), unique=True)
    name = db.Column(db.String(100)) 
    surname = db.Column(db.String(100))
    phone = db.Column(db.String(50))

    rodo = db.Column(db.DateTime) #, server_default=func.now())
    coc = db.Column(db.DateTime)  # code of conduct

    admin = db.Column(db.Integer, default=0)
    # 0 - normal user
    # 1 - jodo
    # 2 - iaido
    # 3 - 1 + 2 - iaido + jodo
    # 4 - kendo
    # 5 - 1 + 4 - kendo + jodo
    # 6 - 2 + 4 - kendo + iaido
    # 7 - 1 + 2 + 4 - all - admin

    # flask login
    is_active = db.Column(db.Boolean, default=True)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_id(self):
        return str(self.id)


class Player(db.Model):
    '''player table model'''
    id = db.Column(db.Integer, primary_key=True)
    u = db.relationship('User', backref=db.backref('items', lazy=True))
    userID = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    name = db.Column(db.String(100))
    pesel = db.Column(db.String(11))
    student = db.Column(db.Boolean, default=False)
    address = db.Column(db.String(50))
    club = db.Column(db.Integer)  # iD in Club table

    licence = db.Column(db.Integer, default=0)  # same as adminz
    title = db.Column(db.Integer, default=0)
    # 0 - zawodnik
    # 1 - II klasa sportowa
    # 2 - I klasa sportowa
    # 3 - klasa mistrzowska
    # 4 - klasa mistrzowska międzynarodowa

    # 1 - renshi, 2 - kyoshi, 3 - hanshi
    kendoshogo = db.Column(db.Integer, default=0) 
    kendo = db.Column(db.Integer, default=0) 
    kendolicence = db.Column(db.DateTime)
    kendolicencehistory = db.Column(db.String(200))

    iaidoshogo = db.Column(db.Integer, default=0)
    iaido = db.Column(db.Integer, default=0) 
    iaidolicence = db.Column(db.DateTime)
    iaidolicencehistory = db.Column(db.String(200))

    jodoshogo = db.Column(db.Integer, default=0)
    jodo = db.Column(db.Integer, default=0) 
    jodolicence = db.Column(db.DateTime)
    jodolicencehistory = db.Column(db.String(200))

    leader = db.Column(db.Boolean, default=False)

    playeriD = db.Column(db.String(10))
    instructor = db.Column(db.String(3))  # iD in Intructor table
    # None - normal player
    # 001 - jodo instructor / intruktor
    # 010 - iaido instructor
    # 100 - kendo instructor
    # 101 - kendo + jodo instructor
    # 110 - kendo + iaido instructor
    # 111 - kendo + iaido + jodo instructor
    #   2 - coach level 2 / trener 2 klasy
    #   3 - coach level 1 / trener 1 klasy
    shimpaniD = db.Column(db.Integer, default=0)  # TODO
    examineriD = db.Column(db.Integer, default=0)  # TODO


class Club(db.Model):
    '''club table model'''
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    abbrev = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    club_key = db.Column(db.String(30), unique=True, nullable=False)
    licence = db.Column(db.DateTime)
    licencehistory = db.Column(db.String(200))
    art = db.Column(db.Integer, default=0) # same as admin