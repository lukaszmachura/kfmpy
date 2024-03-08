import datetime


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
    elif g < 0:
        return f'{-g} kyu'
    else:
        return ''


def shogo(g):
    g = int(g)
    if g == 1:
        return 'Renshi'
    elif g == 2:
        return 'Kyoshi'
    elif g == 3:
        return 'Hanshi'
    return ''