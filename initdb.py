from flask import Flask
from werkzeug.security import generate_password_hash
from models import db, User, Club, Player
from app import app, db
import datetime


def parse_clubs():
    pass


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
            email='user1@user.com',
            name='Useros',
            surname='Oneos',
            rodo=datetime.datetime.now(),
            clubID=3,
            ),
        User(username='tata1', 
            password=generate_password_hash('tata1'),
            email='tata1@user.com',
            name='Jurek',
            surname='Kozakiewicz',
            rodo=datetime.datetime.now(),
            clubID=4,
            ),
        User(username='kido1', 
            password=generate_password_hash('kido1'),
            email='kido1@user.com',
            name='Pietrek',
            surname='Kozakiewicz',
            rodo=datetime.datetime.now(),
            parentID=2,  # id=2 is daddy  <--- not reference just INT
            clubID=4,
            ),
        User(username='admin', 
            password=generate_password_hash('admin'),
            email='admin@user.com',
            name='Admin',
            surname='Super',
            rodo=datetime.datetime.now(),
            clubID=1,
            admin=7),
        User(username='jodo', 
            password=generate_password_hash('jodo'),
            email='jodo@user.com',
            name='Vice',
            surname='Jodo',
            rodo=datetime.datetime.now(),
            clubID=2,
            admin=1),
    ]
    db.session.bulk_save_objects(example)
    db.session.commit()


def create_example_players():
    '''Create example players'''
    example = [
        Player(userID=1,
            name='Useros Oneos',
            kendo='5 dan',
            kendolicence=datetime.datetime.now(),
            kendolicencehistory="24232221201918",
            iaido='2 dan',
            iaidolicence=datetime.datetime(2009, 10, 5, 18, 0),
            iaidolicencehistory="09080704",
            jodo='',
            playeriD='PZK.00001',
            licence=6,
            # instructor="",
            club=3),
        # userID=2 is daddy
        # userID=3 is kido
        Player(userID=3,
            name='Pietrek Kozakiewicz',
            kendo='',
            iaido='3 kyu',
            iaidolicence=datetime.datetime.now(),
            iaidolicencehistory="24",
            jodo='1 dan',
            jodolicence=datetime.datetime(2016, 11, 1, 9, 32),
            jodolicencehistory="161514",
            playeriD='PZK.00002',
            licence=2,
            club=4,
            # instructor=0,
            ),
        Player(userID=4,
            name='Admin Super',
            kendo='6 dan',
            kendolicence=datetime.datetime(2021, 1, 1, 13, 12),
            kendolicencehistory="2120181716151413121109",
            iaido='6 dan',
            iaidolicence=datetime.datetime.now(),
            iaidolicencehistory="2423222120181716151413121109",
            jodo='6 dan',
            jodolicence=datetime.datetime.now(),
            jodolicencehistory="24232221201918171615141312111009080706",
            playeriD='PZK.00003',
            instructor="231",
            licence=7,
            club=1),
        Player(userID=5,
            name='Vice Jodo',
            kendo='',
            iaido='1 dan',
            iaidolicence=datetime.datetime(2022, 10, 21, 18, 0),
            iaidolicencehistory="222120",
            jodo='6 dan',
            jodolicence=datetime.datetime.now(),
            jodolicencehistory="2423222120191817161514131211100908",
            jodoshogo=1,
            playeriD='PZK.00004',
            instructor="001",
            licence=3,
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
        