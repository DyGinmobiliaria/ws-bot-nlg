import requests

def send_to_zapier(phone_number, name, property_interest):
    payload = {
        'phone_number': phone_number,
        'name': name,
        'property_interest': property_interest
    }

    # Enviar los datos a Zapier
    zapier_webhook_url = 'your_zapier_webhook_url'
    response = requests.post(zapier_webhook_url, json=payload)

    if response.status_code == 200:
        print('Datos enviados correctamente a Zapier')
    else:
        print('Error al enviar los datos a Zapier')
