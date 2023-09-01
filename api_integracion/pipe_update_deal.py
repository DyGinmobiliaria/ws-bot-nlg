import requests
import json

url = "https://api.pipedrive.com/v1/deals/6?api_token=8f6fe06a680c20b8f7bb00c704513f1167a0d14e"

payload = json.dumps({
  "stage_id": "8"
})
headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
  'Cookie': '__cf_bm=OnzSeI1FBndxoFILmn0Vobeoz71S9fp6E04Pnet8ChA-1692747443-0-AU6Ef3VBxrr9BSgWlDZQX0iIOOkPVkPaNfbxVhWrElbpYVwmnGBGCIPQPFdie4Dc2vNR08+DsEndH4TKDHmc5jI='
}

response = requests.request("PUT", url, headers=headers, data=payload)

print(response.text)










import requests
import json
import app
API_TOKEN ="8f6fe06a680c20b8f7bb00c704513f1167a0d14e"

person_id = None
ruta_stage = None
id_first_stage = None
id_deal = None
id_final_stage = None
person_name = None
whatsapp_number = None
desarrollo = None
desarrollo_final = None

ruta_stage_a_id_first_stage = {
    'faq_desarrollos/faq_Sant_Maarten.json': '5',
    'faq_desarrollos/faq_kartesia.json': '2',
    'faq_desarrollos/faq_Maria_jose.json': '4',
    'faq_desarrollos/faq_Soneto.json': '3',
    # Agrega más elementos si tienes más archivos y desarrollos asociados
}

ruta_stage_a_id_final_stage = {
    'Sant Maärten Lofts_lead': '7',
    'Sant Maärten Lofts_asesor': '8',
    'Sant Maärten Lofts_cita':'9',

    'Kartesia Residencial_lead': '7',
    'Kartesia Residencial_asesor': '8',
    'Kartesia Residencial_cita':'9',

    'María José Living_lead': '7',
    'María José Living_asesor': '8',
    'María José Living_cita':'9',

    'Soneto Residencial_lead': '7',
    'Soneto Residencial_asesor': '8',
    'Soneto Residencial_cita':'9',
}

def agregar_persona(person_name, whatsapp_number):
  global person_id, id_deal

  if person_name is not None and whatsapp_number is not None:

      url_new_person = f"https://api.pipedrive.com/v1/persons?api_token={API_TOKEN}"

      payload = json.dumps({
        "name": person_name,  # Corregido aquí
        "email": [],
        "phone": [
          {
            "value": whatsapp_number,
            "primary": "True",
            "label": "whatsApp"
          },
        ],
        "visible_to": "1",
        "marketing_status": "1",
      })
      headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Cookie': '__cf_bm=qupb7BVNaJBaXgXyjzBvEa0CvdpIpspf6EhMj7Hv7Y0-1692745252-0-AT9iQLoht9/isbCTkXMyAgiro8ug01JapV1NsFjJPfoOi7uAxEKVh7uR/V3zPT/0zmNJRRjBzMTlo67PrByHsyI='
      }

      response = requests.request("POST", url_new_person, headers=headers, data=payload)

      # Procesar la respuesta JSON
      response_json = response.json()
      if response_json.get("success"):
            person_id = response_json["data"]["id"]
            print(f"ID de persona guardado: {person_id}")
            
      #print(response.text)
      print(f"person_name_add_person_si:", person_name )
      print(f"whatsapp_number_add_person_si:", whatsapp_number )
  else:
    print("No se proporcionaron todos los datos necesarios")
    print(f"person_name_add_person_no:", person_name )
    print(f"whatsapp_number_add_person_no:", whatsapp_number )


  if person_name is not None and person_id is not None:
      url_new_deal = f"https://api.pipedrive.com/v1/deals?api_token={API_TOKEN}"

      payload = json.dumps({
        "title": person_name,
        "person_id": person_id,
        "stage_id": "1",
        "status": "open",
        "label": "WhatsApp-Bot (Panfilo)",
        "visible_to": "3",
        "18320baf08b0aee3d57fc0b26e7b2ab8bc43c7f1": "15",
        "3273fffa7fce003d6c3a9bb4a005f29f70fb5e27": "16"
      })

      headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Cookie': '__cf_bm=UF5_mrFKXmYqrG1mRIRvUaha2Bz0GoSY8hpznUgyY0A-1692746245-0-AWgkoW0JSPLGzolKFgh2dzbpOW21dQjSQC+4tmcvfOaG4MqXK13wTU8M3k64+Rf/wsstQiVlFp3kIkRku4bKaos='
      }

      response = requests.request("POST", url_new_deal, headers=headers, data=payload)
      response_json = response.json()
      if response_json.get("success"):
            id_deal = response_json["data"]["id"]
            print(f"ID de deal guardado: {id_deal}")

      #print(response.text)
  if id_deal is not None:
    url = f"https://api.pipedrive.com/v1/notes?api_token={API_TOKEN}"

    payload = json.dumps({
      "content": f"{person_name} ha dejado sus datos desde el Bot de WhatsApp",
      "deal_id": id_deal
    })
    headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Cookie': '__cf_bm=VzMFgPKLCX96U7A_cmPGT3ughyFzbj7XxqoA5MblWQk-1692834913-0-AbpwgxOCFt38X4wmtw5k3PtcQ3vtiiapdHlqbjSdHGRCd5VKDdwKqjVQXgw++ROvMoPE6IXmxR5EnxsLnN1tdMk='
    }

    response = requests.request("POST", url, headers=headers, data=payload)

  print(response.text)    

def update_deal(person_name, ruta_stage, desarrollo):
  global id_first_stage
  id_first_stage = ruta_stage_a_id_first_stage.get(ruta_stage)
  desarrollo = desarrollo
  if id_deal is not None and id_first_stage is not None:
    url_update_deal = f"https://api.pipedrive.com/v1/deals/{id_deal}?api_token={API_TOKEN}"
    print(f"link con deal:",url_update_deal)
  
    payload = json.dumps({
      "stage_id": id_first_stage
    })
    headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Cookie': '__cf_bm=OnzSeI1FBndxoFILmn0Vobeoz71S9fp6E04Pnet8ChA-1692747443-0-AU6Ef3VBxrr9BSgWlDZQX0iIOOkPVkPaNfbxVhWrElbpYVwmnGBGCIPQPFdie4Dc2vNR08+DsEndH4TKDHmc5jI='
    }

    response = requests.request("PUT", url_update_deal, headers=headers, data=payload)

    #print(response.text)
    print(f"url_update_deal_si:", url_update_deal )
    print(f"id_first_stage_si:", id_first_stage )
  else:
    print("No se proporcionaron todos los datos ruta_stage")
    print(f"url_update_deal_no:", url_update_deal )
    print(f"id_first_stage_no:", id_first_stage )

  if ruta_stage is not None:
    url = f"https://api.pipedrive.com/v1/notes?api_token={API_TOKEN}"

    payload = json.dumps({
      "content": f"A {person_name} le ha interesado {desarrollo}",
      "deal_id": id_deal
    })
    headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Cookie': '__cf_bm=VzMFgPKLCX96U7A_cmPGT3ughyFzbj7XxqoA5MblWQk-1692834913-0-AbpwgxOCFt38X4wmtw5k3PtcQ3vtiiapdHlqbjSdHGRCd5VKDdwKqjVQXgw++ROvMoPE6IXmxR5EnxsLnN1tdMk='
    }

    response = requests.request("POST", url, headers=headers, data=payload)

  print(response.text)


def final_position_deal_cita (person_name, desarrollo_final, dia_cita, hora_cita):
  global id_final_stage
  id_final_stage = ruta_stage_a_id_final_stage.get(desarrollo_final)

  if id_deal is not None and id_final_stage is not None:
    url_update_deal = f"https://api.pipedrive.com/v1/deals/{id_deal}?api_token={API_TOKEN}"
    print(f"link con deal:",url_update_deal)
  
    payload = json.dumps({
      "stage_id": id_final_stage,
      "user_id": "14754983"
    })
    headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Cookie': '__cf_bm=OnzSeI1FBndxoFILmn0Vobeoz71S9fp6E04Pnet8ChA-1692747443-0-AU6Ef3VBxrr9BSgWlDZQX0iIOOkPVkPaNfbxVhWrElbpYVwmnGBGCIPQPFdie4Dc2vNR08+DsEndH4TKDHmc5jI='
    }

    response = requests.request("PUT", url_update_deal, headers=headers, data=payload)

    #print(response.text)
    print(f"url_update_deal_si:", url_update_deal )
    print(f"id_first_stage_si:", id_first_stage )
  else:
    print("No se proporcionaron todos los datos ruta_stage")
    print(f"url_update_deal_no:", url_update_deal )
    print(f"id_first_stage_no:", id_first_stage )

  if id_final_stage is not None:
    url = f"https://api.pipedrive.com/v1/notes?api_token={API_TOKEN}"

    payload = json.dumps({
      "content": f"{person_name} ha pedido una cita el día: {dia_cita} a las: {hora_cita}",
      "deal_id": id_deal
    })
    headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Cookie': '__cf_bm=VzMFgPKLCX96U7A_cmPGT3ughyFzbj7XxqoA5MblWQk-1692834913-0-AbpwgxOCFt38X4wmtw5k3PtcQ3vtiiapdHlqbjSdHGRCd5VKDdwKqjVQXgw++ROvMoPE6IXmxR5EnxsLnN1tdMk='
    }

    response = requests.request("POST", url, headers=headers, data=payload)

  print(response.text)





def final_position_deal_asesor (person_name, desarrollo_final):
  global id_final_stage
  id_final_stage = ruta_stage_a_id_final_stage.get(desarrollo_final)

  if id_deal is not None and id_final_stage is not None:
    url_update_deal = f"https://api.pipedrive.com/v1/deals/{id_deal}?api_token={API_TOKEN}"
    print(f"link con deal:",url_update_deal)
  
    payload = json.dumps({
      "stage_id": id_final_stage,
      "user_id": "14754983"
    })
    headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Cookie': '__cf_bm=OnzSeI1FBndxoFILmn0Vobeoz71S9fp6E04Pnet8ChA-1692747443-0-AU6Ef3VBxrr9BSgWlDZQX0iIOOkPVkPaNfbxVhWrElbpYVwmnGBGCIPQPFdie4Dc2vNR08+DsEndH4TKDHmc5jI='
    }

    response = requests.request("PUT", url_update_deal, headers=headers, data=payload)

    #print(response.text)
    print(f"url_update_deal_si:", url_update_deal )
    print(f"id_first_stage_si:", id_first_stage )
  else:
    print("No se proporcionaron todos los datos ruta_stage")
    print(f"url_update_deal_no:", url_update_deal )
    print(f"id_first_stage_no:", id_first_stage )

  if id_final_stage is not None:
    url = f"https://api.pipedrive.com/v1/notes?api_token={API_TOKEN}"

    payload = json.dumps({
      "content": f"{person_name} ha pedido una asesoramiento sonbre {desarrollo_final}",
      "deal_id": id_deal
    })
    headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Cookie': '__cf_bm=VzMFgPKLCX96U7A_cmPGT3ughyFzbj7XxqoA5MblWQk-1692834913-0-AbpwgxOCFt38X4wmtw5k3PtcQ3vtiiapdHlqbjSdHGRCd5VKDdwKqjVQXgw++ROvMoPE6IXmxR5EnxsLnN1tdMk='
    }

    response = requests.request("POST", url, headers=headers, data=payload)

  print(response.text)




def final_position_deal_lead (person_name, desarrollo_final):
  global id_final_stage
  id_final_stage = ruta_stage_a_id_final_stage.get(desarrollo_final)

  if id_deal is not None and id_final_stage is not None:
    url_update_deal = f"https://api.pipedrive.com/v1/deals/{id_deal}?api_token={API_TOKEN}"
    print(f"link con deal:",url_update_deal)
    payload = json.dumps({
      "stage_id": id_final_stage,
    })
    headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Cookie': '__cf_bm=OnzSeI1FBndxoFILmn0Vobeoz71S9fp6E04Pnet8ChA-1692747443-0-AU6Ef3VBxrr9BSgWlDZQX0iIOOkPVkPaNfbxVhWrElbpYVwmnGBGCIPQPFdie4Dc2vNR08+DsEndH4TKDHmc5jI='
    }

    response = requests.request("PUT", url_update_deal, headers=headers, data=payload)

    #print(response.text)
    print(f"url_update_deal_si:", url_update_deal )
    print(f"id_first_stage_si:", id_first_stage )
  else:
    print("No se proporcionaron todos los datos ruta_stage")
    print(f"url_update_deal_no:", url_update_deal )
    print(f"id_first_stage_no:", id_first_stage )

  if id_final_stage is not None:
    url = f"https://api.pipedrive.com/v1/notes?api_token={API_TOKEN}"

    payload = json.dumps({
      "content": f"El bot no pudo ayudar a {person_name}, sobre el desarrollo: {desarrollo_final}",
      "deal_id": id_deal
    })
    headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Cookie': '__cf_bm=VzMFgPKLCX96U7A_cmPGT3ughyFzbj7XxqoA5MblWQk-1692834913-0-AbpwgxOCFt38X4wmtw5k3PtcQ3vtiiapdHlqbjSdHGRCd5VKDdwKqjVQXgw++ROvMoPE6IXmxR5EnxsLnN1tdMk='
    }

    response = requests.request("POST", url, headers=headers, data=payload)

  print(response.text)