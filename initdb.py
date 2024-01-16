from flask import Flask
from werkzeug.security import generate_password_hash
from models import db, User, Club
from app import app, db

def add_clubs():
    '''Add three examples of clubs to the database'''
    example_clubs = [
        Club(name='Bumeikan', city='Katowice', email='pzk@bumeikan.pl', club_key='bumkat'),
        Club(name='WSK', city='Wrocław', email='wiesiek@wsk.pl', club_key='wskwro'),
        Club(name='WKK', city='Warszawa', email='boss@kendo.wawa.pl', club_key='wkkwar'),
    ]

    db.session.bulk_save_objects(example_clubs)
    db.session.commit()

# Create two example users
def create_example_users():
    user1 = User(username='user1', 
                    password=generate_password_hash('pass1'),
                    kendo='5 dan',
                    iaido='2 dan',
                    jodo='',
                    club=3)
    user2 = User(username='user2', 
                    password=generate_password_hash('pass2'),
                    kendo='',
                    iaido='5 dan',
                    jodo='6 dan',
                    club=2)
    admin = User(username='admin', 
                    password=generate_password_hash('passa'),
                    kendo='',
                    iaido='6 dan',
                    jodo='6 dan',
                    club=1)

    db.session.add(user1)
    db.session.add(user2)
    db.session.add(admin)
    db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        create_example_users()
        print('Example users added to the database.')
        
        add_clubs()
        print('Example clubs added to the database.')
