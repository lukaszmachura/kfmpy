import requests
import json
import time, datetime
import os


def get_credentials(client_id="477482", client_secret="fd6ca32d3d2e7466f103167d21df4ccd"):
    url = "https://secure.snd.payu.com/pl/standard/user/oauth/authorize"
    
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


def get_kendo_licence(client_id, access_token):
    url = "https://secure.snd.payu.com/api/v2_1/orders"

    params = {
        "notifyUrl": "http://kendo.pl",
        "customerIp": "127.0.0.1",
        "merchantPosId": str(client_id),
        "description": "Licencja zawodnicza PZK",
        "currencyCode": "PLN",
        "totalAmount": "20000",
        "extOrderId": f"pzklic24{int(time.time() * 100)}",
        "buyer": {
            "email": "ulgotbulgot@gmail.com",
            "phone": "654111654",
            "firstName": "John",
            "lastName": "Doe",
            "language": "pl"
        },
        "products": [
            {
                "name": "Licencja kendo",
                "unitPrice": "15000",
                "quantity": "1"
            },
            {
                "name": "Biuro",
                "unitPrice": "5000",
                "quantity": "1"
            }
        ]
    }

    headers = {
        "Accept": "application/json", 
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Bearer {access_token}"
        }
    
    response = requests.post(url, data=params, headers=headers)
    if response.status_code == 200:
        return response
    else:
        return "dupa"


def pauy_order_curl(client_id, access_token, amount=100, player_info={}):
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
    fname = '.pzkpayu' + UNIQUE_ID
    order_id = f'pzklic{datetime.datetime.now().year}{player_name}'

    CURLCOM = f'''curl -X POST https://secure.snd.payu.com/api/v2_1/orders \\
    -H "Content-Type: application/json" \\
    -H "Authorization: Bearer {access_token}" \\
    -d '{{
        "notifyUrl": "http://127.0.0.1:5000",
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

        "products": [
            {{
                "name": "Licencja",                    
                "unitPrice": "{int(amount * 100)}",
                "quantity": "1"
            }}
        ]
    }}' > {fname}'''
    
    os.system(CURLCOM)
    with open(fname) as f:
        j = f.read()
    os.system('rm ' + fname)

    return j


def get_redirect_uri(client_id=None, client_secret=None, amount=100, player_info={}):
    '''
    in case of client_id or client secret empty 
    use LM's sandbox
    '''

    if client_id == None or client_secret == None:
        client_id = "477482"
        client_secret = "fd6ca32d3d2e7466f103167d21df4ccd"

    response = get_credentials(client_id, client_secret)
    response = json.loads(response.content)
    access_token = response["access_token"]

    # response = get_kendo_curl(client_id, access_token, amount, player_info)
    response = pauy_order_curl(client_id, access_token, amount, player_info)
    response = json.loads(response)
    redirect_uri = response["redirectUri"]
    
    return redirect_uri


if __name__ == "__main__":
    redirect_uri = get_redirect_uri()
    print(redirect_uri)
    
    


