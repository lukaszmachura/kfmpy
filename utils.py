from datetime import datetime


def date_formatter(year, month, day):
    birthdate = datetime(year, month, day)
    return birthdate.strftime("%Y-%m-%d")


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
    gender = "K" if pesel[9] % 2 == 0 else "M"
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
    pesel = "86062518837"  # Zastąp tym rzeczywistym numerem PESEL
    birthdate = pesel_to_birthdate(pesel)
    print("Data urodzenia:", birthdate)

    result = pesel_to_birthdate_and_gender(pesel)
    print("Wynik:", result)
    
    print("Is valid PESEL:", is_valid_pesel(pesel))


