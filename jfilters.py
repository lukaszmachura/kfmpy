import datetime


def ymd(date):
    miesiace_dopelniacz = {
        1: "stycznia",
        2: "lutego",
        3: "marca",
        4: "kwietnia",
        5: "maja",
        6: "czerwca",
        7: "lipca",
        8: "sierpnia",
        9: "września",
        10: "października",
        11: "listopada",
        12: "grudnia"
    }
    ret = f"{date.day} {miesiace_dopelniacz[date.month]} {date.year}"
    return ret  #str(date.year) + '.' + str(date.month) + '.' + str(date.day)


def is_older_than_one_year(date):
    if date == None:
        return True
    
    if date == "None":
        return True
    
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