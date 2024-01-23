from flask import Flask
from werkzeug.security import generate_password_hash
from models import db, User, Club, Player
from app import app, db


def add_clubs():
    '''Add three examples of clubs to the database'''
    example_clubs = [
        Club(name='PZK', city='Łódź', email='pzk@kendo.pl', club_key='pzklod'),
        Club(name='Bumeikan', city='Katowice', email='pzk@bumeikan.pl', club_key='bumkat'),
        Club(name='WSK', city='Wrocław', email='wiesiek@wsk.pl', club_key='wskwro'),
        Club(name='WKK', city='Warszawa', email='boss@kendo.wawa.pl', club_key='wkkwar'),
    ]

    db.session.bulk_save_objects(example_clubs)
    db.session.commit()


def create_example_users():
    '''Create example users'''
    example = [
        User(username='user1', 
            password=generate_password_hash('user1'),
            ),
        User(username='tata1', 
            password=generate_password_hash('tata1'),
            name='Jurek',
            surname='Kozakiewicz',
            ),
        User(username='kido1', 
            password=generate_password_hash('kido1'),
            name='Pietrek',
            surname='Kozakiewicz',
            parentID=2,  # id=2 is daddy  <--- not reference just INT
            ),
        User(username='admin', 
            password=generate_password_hash('admin'),
            admin=7),
        User(username='jodo', 
            password=generate_password_hash('jodo'),
            admin=1),
    ]
    db.session.bulk_save_objects(example)
    db.session.commit()


def create_example_players():
    '''Create example players'''
    example = [
        Player(userID=1,
            kendo='5 dan',
            iaido='2 dan',
            jodo='',
            playeriD='PZK.00001',
            club=3),
        # userID=2 is daddy
        # userID=3 is kido
        Player(userID=3,
                kendo='',
                iaido='6 dan',
                jodo='6 dan',
                playeriD='PZK.00002',
                club=4,
                ),
        Player(userID=4,
                kendo='6 dan',
                iaido='6 dan',
                jodo='6 dan',
                playeriD='PZK.00003',
                club=1),
        Player(userID=5,
                kendo='',
                iaido='6 dan',
                jodo='6 dan',
                playeriD='PZK.00004',
                club=2),
    ]

    db.session.bulk_save_objects(example)
    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        add_clubs()
        print('Example clubs added to the database.')

        create_example_users()
        print('Example users added to the database.')
        
        create_example_players()
        print('Example players added to the database.')
        