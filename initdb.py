from flask import Flask
from werkzeug.security import generate_password_hash
from models import db, User, Club, Player
from app import app, db
import datetime
from utils import parse_csv, parse_club_csv, get_playeriD


def parse_users():
    file = 'players.csv'
    data = parse_csv(file)
    users = []
    for row in data[:33]:
        # Ensure all required columns are present
        if all(col in row for col in ['username', 'password', 'clubID', 'fname', 'surname']):
            users.append(
                User(
                    username=row.get('username'),
                    password=generate_password_hash(row.get('password')),
                    parentID=row.get('parentID') if row.get('parentID') else None,
                    clubID=row.get('clubID') if row.get('clubID') else None,
                    leader=bool(row.get('leader')) if row.get('leader') else False,
                    email=row.get('email') if row.get('email') else None,
                    name=row.get('fname') if row.get('fname') else None,
                    surname=row.get('surname') if row.get('surname') else None,
                    phone=row.get('phone') if row.get('phone') else None,
                    admin=row.get('admin') if row.get('admin') else 0,
                )
            )
    db.session.bulk_save_objects(users)
    db.session.commit()


def parse_players():
    file = 'players.csv'
    data = parse_csv(file)
    players = []
    for idx, row in enumerate(data[:33]):
        # Ensure all required columns are present
        if all(col in row for col in ['name', 'clubID']):
            players.append(
                Player(
                    userID=idx+1,
                    name=row.get('name') if row.get('name') else None,
                    student=bool(row.get('student')) if row.get('student') else False,
                    club=row.get('clubID') if row.get('clubID') else None,
                    licence=row.get('licence') if row.get('licence') else 0,
                    title=row.get('title') if row.get('title') else 0,

                    kendoshogo=row.get('kendoshogo') if row.get('kendoshogo') else 0, 
                    kendo=row.get('kendo') if row.get('kendo') else None,
                    kendolicence=datetime.datetime.strptime(row.get('kendolicence'), '%Y-%m-%d') if row.get('kendolicence') else None,
                    kendolicencehistory=row.get('kendolicencehistory') if row.get('kendolicencehistory') else None,

                    iaidoshogo=row.get('iaidoshogo') if row.get('iaidoshogo') else 0, 
                    iaido=row.get('iaido') if row.get('iaido') else None,
                    iaidolicence=datetime.datetime.strptime(row.get('iaidolicence'), '%Y-%m-%d') if row.get('iaidolicence') else None,
                    iaidolicencehistory=row.get('iaidolicencehistory') if row.get('iaidolicencehistory') else None,

                    jodoshogo=row.get('jodoshogo') if row.get('jodoshogo') else 0, 
                    jodo=row.get('jodo') if row.get('jodo') else None,
                    jodolicence=datetime.datetime.strptime(row.get('jodolicence'), '%Y-%m-%d') if row.get('jodolicence') else None,
                    jodolicencehistory=row.get('jodolicencehistory') if row.get('jodolicencehistory') else None,

                    leader=bool(row.get('leader')) if row.get('leader') else False,
                    playeriD=get_playeriD(idx+1),
                    instructor=row.get('instructor') if row.get('instructor') else None,
                )
            )
    db.session.bulk_save_objects(players)
    db.session.commit()


def parse_clubs():
    file = 'clubs.csv'
    clubs = parse_club_csv(file)
    clubs = [
        Club(
            name=c.get('name', None),
            abbrev=c.get('abbrev', None),
            city=c.get('city', None),
            club_key=c.get('club_key', None),
            email=c.get('email', None),
            licence=c.get('licence',datetime.datetime(2020, 1, 1, 0, 0)),
            licencehistory=c.get('licencehistory',""),
            art=int(c.get('art', 0)),
        )
        for c in clubs
    ]
    db.session.bulk_save_objects(clubs)
    db.session.commit()


def add_clubs():
    '''Add three examples of clubs to the database'''
    example_clubs = [
        Club(name='Polski Związek Kendo', abbrev='PZK', 
             licence=datetime.datetime(2024, 1, 1, 0, 0),
             licencehistory='2423222120',
             city='Łódź', email='pzk@kendo.pl', club_key='pzklod'),
        Club(name='Klub Sportowy Bumeikan', abbrev='Bumeikan', 
             licence=datetime.datetime(2024, 1, 5, 18, 0),
             licencehistory='242322212019181716151413121110090807',
             city='Katowice', email='pzk@bumeikan.pl', club_key='bumkat'),
        Club(name='Wrocławskie Stowarzyszenie Kendo', abbrev='WSK', 
             licence=datetime.datetime(2024, 1, 1, 1, 0),
             licencehistory='2423222120191817161514131211100908070605',
             city='Wrocław', email='wiesiek@wsk.pl', club_key='wskwro'),
        Club(name='Warszawski Klub Kendo', abbrev='WKK', city='Warszawa', 
             licence=datetime.datetime(2024, 1, 12, 11, 12),
             licencehistory='242322212019181716',
             email='boss@kendo.wawa.pl', club_key='wkkwar'),
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
            # rodo=datetime.datetime.now(),
            clubID=3,
            leader=True,
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

        # add_clubs()
        parse_clubs()
        print('PZK clubs added to the database')

        # # create_example_users()
        parse_users()
        print('PZK users added to the database')
        
        # # create_example_players()
        parse_players()
        print('Example players added to the database')
        