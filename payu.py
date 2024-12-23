import requests
import json
import time, datetime
import os
from pzkconfig import licencje
from config import *

from flask import url_for


def get_credentials(client_id=None, client_secret=None):
    url = "https://secure.snd.payu.com/pl/standard/user/oauth/authorize"
    
    if client_id == None or client_secret == None:
        # read credentials from config file
        client_id = SAND_CLIENT_ID  # LM's sandbox
        client_secret = SAND_CLIENT_SECRET

    params = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
    }
    headers = {
        "Accept": "application/json", 
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    response = requests.request("POST", url, data=params, headers=headers)
    return response


def order_status(orderId, access_token):
    # curl -X GET https://secure.payu.com/api/v2_1/orders/{orderId} \
    # -H "Content-Type: application/json" \
    # -H "Authorization: Bearer 3e5cac39-7e38-4139-8fd6-30adc06a61bd" \

    url = "https://secure.snd.payu.com/api/v2_1/orders/" + orderId
    
    headers = {
        "Authorization": f"Bearer {access_token}", 
        "Content-Type": "application/json"
    }
    
    response = requests.request("GET", url, headers=headers)
    return response


def get_order_status(client_id=None, client_secret=None, order_id=None):
    '''
    in case of client_id or client secret empty 
    use LM's sandbox
    '''

    if client_id == None or client_secret == None:
        # read credentials from config file
        client_id = SAND_CLIENT_ID  # LM's sandbox
        client_secret = SAND_CLIENT_SECRET

    response = get_credentials(client_id, client_secret)
    response = json.loads(response.content)
    access_token = response["access_token"]

    response = order_status(order_id, access_token)
    response = json.loads(response.content)
    
    return response


def get_kendo_licence(client_id, access_token, amount=100, player_info={}):
    url = "https://secure.snd.payu.com/api/v2_1/orders"

    if player_info:
        first_name = player_info.get('user').name.capitalize()
        last_name = player_info.get('user').surname.capitalize()
    else:
        first_name = 'John'
        last_name = 'Doe'
    player_name = first_name + last_name
    
    if player_info.get('user').email:
        email = player_info.get('user').email.lower()
    else:
        email = 'dev@null.com'

    if player_info.get('user').phone:
        phone_number = player_info.get('user').phone
    else:
        phone_number = '123123123'
    
    UNIQUE_ID = str(int(time.time() * 100))
    order_id = f'pzklic{datetime.datetime.now().year}{player_name}'

    params = {
        "continueUrl": "http://127.0.0.1:5000/continue",
        "notifyUrl": "http://127.0.0.1:5000/notify",
        "customerIp": "127.0.0.1",
        "merchantPosId": f"{client_id}",
        "description": f"{order_id}",
        "currencyCode": "PLN",
        "totalAmount": f"{int(amount * 100)}",
        "extOrderId": f"{order_id + UNIQUE_ID}",
        "buyer": {
            "email": f"{email}",
            "phone": f"{phone_number}",
            "firstName": f"{first_name}",
            "lastName": f"{last_name}",
            "language": "pl"
        },
        "products": [
            {
                "name": "Licencja",
                "unitPrice": f"{int(amount * 100)}",
                "quantity": "1"
            }
        ]
    }

    headers = {
        # "Accept": "application/json", 
        "Content-Type": "application/json", #"application/x-www-form-urlencoded",
        "Authorization": f"Bearer {access_token}"
        }
    
    response = requests.post(url, data=params, headers=headers)
    if response.status_code == 200:
        return response
    else:
        return "dupa"


def payu_order_curl(client_id, access_token, amount=100, player_info={}):
    '''
    CURL hack for placing an order in PayU system
    '''

    if player_info:
        first_name = player_info.get('user').name.capitalize()
        last_name = player_info.get('user').surname.capitalize()
    else:
        first_name = 'John'
        last_name = 'Doe'
    player_name = first_name + last_name
    
    if player_info.get('user').email:
        email = player_info.get('user').email.lower()
    else:
        email = 'dev@null.com'

    if player_info.get('user').phone:
        phone_number = player_info.get('user').phone
    else:
        phone_number = '123123123'

    kendo = iaido = jodo = 0
    lic = player_info.get('licences')
    if lic:
        kendo = licencje['kendo'] if 'k' in lic else 0
        iaido = licencje['iaido'] if 'i' in lic else 0
        jodo = licencje['jodo'] if 'j' in lic else 0
    
    UNIQUE_ID = str(int(time.time() * 100))
    fname = '.pzkpayu' + UNIQUE_ID
    order_id = f'pzklic{datetime.datetime.now().year}{player_name}'

    CURLCOM = f'''curl -X POST https://secure.snd.payu.com/api/v2_1/orders \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer {access_token}" \\
    -d '{{
        "continueUrl": "http://127.0.0.1:5000/continue",
        "notifyUrl": "http://127.0.0.1:5000/notify",
        "customerIp": "127.0.0.1",
        "merchantPosId": "{client_id}",
        "description": "{order_id}",
        "currencyCode": "PLN",
        "totalAmount": "{int(amount * 100)}",
        "extOrderId": "{order_id + UNIQUE_ID}",
     
        "buyer": {{
            "email": "{email}",
            "phone": "{phone_number}",
            "firstName": "{first_name}",
            "lastName": "{last_name}",
            "language": "pl"
        }},

        "products": ['''
    
    prod = f'''
            {{
                "name": "Administracja",                    
                "unitPrice": "{int(licencje['admin'] * 100)}",
                "quantity": "1"
            }},'''
    
    if kendo:
        prod += f'''
            {{
                "name": "Kendo",                    
                "unitPrice": "{int(licencje['kendo'] * 100)}",
                "quantity": "1"
            }},'''
    
    if iaido:
        prod += f'''
            {{
                "name": "Iaido",                    
                "unitPrice": "{int(licencje['iaido'] * 100)}",
                "quantity": "1"
            }},'''
        
    if jodo:
        prod += f'''
            {{
                "name": "Jodo",                    
                "unitPrice": "{int(licencje['jodo'] * 100)}",
                "quantity": "1"
            }},'''
    
    CURLCOM += prod[:-1]
  
    CURLCOM += f'''
        ]
    }}' > {fname}'''
    
    os.system(CURLCOM)
    with open(fname) as f:
        order = f.read()
    os.system('rm ' + fname)

    return order


def place_payu_order(client_id=None, client_secret=None, amount=100, player_info={}):
    '''
    in case of client_id or client secret empty 
    use LM's sandbox
    '''

    if client_id == None or client_secret == None:
        # read credentials from config file
        client_id = SAND_CLIENT_ID  # LM's sandbox
        client_secret = SAND_CLIENT_SECRET

    response = get_credentials(client_id, client_secret)
    response = json.loads(response.content)
    access_token = response["access_token"]

    response = payu_order_curl(client_id, access_token, amount, player_info)
    response = json.loads(response)
    # redirect_uri = response["redirectUri"]
    
    return response


if __name__ == "__main__":
    class TmpUser:
        def __init__(self, name, surname, email, phone):
            self.name = name
            self.surname = surname
            self.email = email
            self.phone = phone

    u = TmpUser('Joe', 'Doe', 'joe@doe.com', '123123123')
    response = place_payu_order(player_info={'user': u, 'licences': 'ij'})
    print(response)

    response = get_order_status(order_id=response['orderId'])
    print(response)
    
    # response = get_order_status(order_id='???')
    # print(response)

