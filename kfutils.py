# utility functions 4 kendo federation
import datetime
from flask import flash
from markupsafe import escape
from jfilters import *
from utils import *


def set_licence_date(date):
    date = escape(date)
    if date:
        date = datetime.datetime.strptime(date, '%Y-%m-%d')
    else:
        date = datetime.datetime(2000, 1, 1, 0, 0)
    return date


def kf_test_grade_shogo(grade, shogo):
    assert isinstance(grade, int), 'dan grade should be INT'
    assert isinstance(shogo, int), 'shogo should be [0, 3]'
    if grade == 6 and shogo <= 1:
        return True
    elif grade == 7 and shogo <= 2:
        return True
    elif grade == 8 and shogo <= 3:
        return True
    return False


def number_from_form(grade):
    grade = escape(grade)
    grade = clean_input(grade)
    if isinstance(grade, int):
        return grade
    elif isinstance(grade, str) and grade.isnumeric():
        return int(grade)
    else:
        return 0
    

def grade_from_form(grade):
    return number_from_form(grade)


def kf_licence(player):
    num = 0 
    if not is_older_than_one_year(player.kendolicence):
        num += 4
    if not is_older_than_one_year(player.iaidolicence):
        num += 2
    if not is_older_than_one_year(player.jodolicence):
        num += 1
    return num


def set_shogo(player, sgrade, art):
    sgrade = number_from_form(sgrade)
    if sgrade and player.__dict__[art]: 
        if kf_test_grade_shogo(player.__dict__[art], sgrade):
            return sgrade
        else:
            flash(f'{player.name}: zbyt niski stopień {dan(player.__dict__[art])} dla shogo {shogo(sgrade)}', 'error')
            return player.__dict__[art+'shogo']
    return 0
    