licencje = {
    'admin': 50,
    'kendo': 150,
    'iaido': 150,
    'jodo': 150,
    'instruktor': 100
}

def licence_db_number(info):
    num = 0
    if 'j' in info:
        num += 1
    if 'i' in info:
        num += 2
    if 'k' in info:
        num += 4
    return num