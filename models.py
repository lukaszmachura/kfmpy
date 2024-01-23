from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model, UserMixin):
    '''user table model'''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    rodo = db.Column(db.Boolean, default=False)
    coc = db.Column(db.Boolean, default=False)  # code of conduct

    parentID = db.Column(db.Integer)  # make this local reference
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))

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

    pesel = db.Column(db.String(11))
    city = db.Column(db.String(50))
    phone = db.Column(db.String(50))
    club = db.Column(db.Integer)  # iD in Club table

    licence = db.Column(db.Integer, default=0)

    kendo = db.Column(db.String(50))
    kendoshogo = db.Column(db.Integer, default=0)
    iaido = db.Column(db.String(50))
    iaidoshogo = db.Column(db.Integer, default=0)
    jodo = db.Column(db.String(50))
    jodoshogo = db.Column(db.Integer, default=0)

    leader = db.Column(db.Boolean, default=False)

    playeriD = db.Column(db.String(10))
    instructoriD = db.Column(db.Integer, default=0)  # iD in Intructor table
    shimpaniD = db.Column(db.Integer, default=0)  # TODO
    examinatoriD = db.Column(db.Integer, default=0)  # TODO


class Club(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=True)    
    club_key = db.Column(db.String(30), unique=True, nullable=False)
