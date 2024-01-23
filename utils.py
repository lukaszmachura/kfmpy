from datetime import datetime

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

    # Zbuduj datę i zwróć w odpowiednim formacie
    birthdate = datetime(year, month, day)
    return birthdate.strftime("%d-%m-%Y")


from datetime import datetime

def pesel_to_birthdate_and_gender(pesel):
    # Sprawdź czy PESEL ma poprawną długość
    if len(pesel) != 11:
        return "Nieprawidłowa długość PESEL"

    # Wyciągnij rok, miesiąc, dzień i płeć z PESEL
    year = int(pesel[0:2])
    month = int(pesel[2:4])
    day = int(pesel[4:6])
    gender_digit = int(pesel[9])

    # Sprawdź stulecie na podstawie miesiąca
    if month > 20:
        year += 2000
        month -= 20
    elif month > 12:
        year += 1900
        month -= 10
    else:
        year += 1900

    # Określ płeć
    gender = "K" if gender_digit % 2 == 0 else "M"

    # Zbuduj datę i zwróć w odpowiednim formacie
    birthdate = datetime(year, month, day)
    return {"Data urodzenia": birthdate.strftime("%d-%m-%Y"), "Płeć": gender}


if __name__ == '__main__':
    pesel = "86062518837"  # Zastąp tym rzeczywistym numerem PESEL
    birthdate = pesel_to_birthdate(pesel)
    print("Data urodzenia:", birthdate)
    result = pesel_to_birthdate_and_gender(pesel)
    print("Wynik:", result)

