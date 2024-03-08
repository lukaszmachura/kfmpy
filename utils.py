import datetime
import csv


def clean_input(s):
    if isinstance(s, str):
        if s == 'None':  # escaped None
            return None
        else:
            if len(s) == 3:  # licence
                return s
            else:  # grades, admins...
                try:
                    return int(s)
                except ValueError:
                    return None
    return s


def parse_csv(filepath):
    with open(filepath, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = []
        for row in reader:
            data.append(row)
    return data


def parse_club_csv(file_path):
    """
    Parses a CSV file with specific columns: name, abbrev, city, club_key, email, licence, licencehistory.
    
    Parameters:
    - file_path: The path to the CSV file.
    
    Returns:
    - A list of dictionaries, where each dictionary contains the data of a row.
    """
    data = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Ensure all required columns are present
            if all(col in row for col in ['name', 'abbrev', 'city', 'club_key', 'email', 'licence', 'licencehistory', 'art']):
                data.append({
                    'name': row['name'],
                    'abbrev': row['abbrev'],
                    'city': row['city'],
                    'club_key': row['club_key'],
                    'email': row['email'],
                    'licence': datetime.datetime.strptime(row['licence'], '%Y-%m-%d'),
                    'licencehistory': row['licencehistory'],
                    'art': row['art']
                })
            else:
                # Handle the case where some columns are missing or there's a mismatch
                print("Warning: Some columns are missing or there's a mismatch in the row:", row)
    
    return data


def date_formatter(year, month, day):
    date = datetime.datetime(year, month, day)
    return date.strftime("%Y-%m-%d")


def pesel_to_birthdate(pesel):
    # Sprawdź czy PESEL ma poprawną długość
    if len(pesel) != 11:
        return "Nieprawidłowa długość PESEL"

    # Wyciągnij rok, miesiąc i dzień z PESEL
    year = int(pesel[0:2])
    month = int(pesel[2:4])
    day = int(pesel[4:6])

    # Sprawdź stulecie na podstawie miesiąca
    if month > 20:
        year += 2000
        month -= 20
    elif month > 12:
        year += 1900
        month -= 10
    else:
        year += 1900

    return year, month, day


def pesel_to_birthdate_and_gender(pesel):
    p = pesel_to_birthdate(pesel)
    gender = "K" if int(pesel[9]) % 2 == 0 else "M"
    return {"date": date_formatter(*p), "sex": gender}


def is_valid_pesel(pesel):
    # Check if PESEL has proper length
    if len(pesel) != 11:
        return False

    # Check if all characters are digits
    if not pesel.isdigit():
        return False

    # Calculate control sum
    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    control_sum = sum(int(pesel[i]) * weights[i] for i in range(10))
    control_digit = (10 - (control_sum % 10)) % 10

    # Compare calculated control digit with the one from PESEL
    return control_digit == int(pesel[10])


def get_playeriD(n):
    return f"PZK.{n:05}"


if __name__ == '__main__':
    # pesel = "86062518837"  # Zastąp tym rzeczywistym numerem PESEL
    # birthdate = pesel_to_birthdate(pesel)
    # print("Data urodzenia:", birthdate)

    # result = pesel_to_birthdate_and_gender(pesel)
    # print("Wynik:", result)
    
    # print("Is valid PESEL:", is_valid_pesel(pesel))

    # file_path = 'clubs.csv'
    # parsed_data = parse_csv(file_path)
    # print(parsed_data)

    filepath = 'players.csv'  # Update this to the path of your CSV file
    data = parse_csv(filepath)

    # Example usage: print the first row (if there is one)
    if data:
        print(data[0].keys())
        print(data[0:2])
    else:
        print("No data found.")