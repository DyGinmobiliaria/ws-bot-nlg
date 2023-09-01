import requests
import json
import app
from config import PIPEDRIVE_API_KEY
PIPEDRIVE_API_KEY = PIPEDRIVE_API_KEY

person_id = None
ruta_stage = None
id_first_stage = None
id_deal = None
id_final_stage = None
person_name = None
whatsapp_number = None
desarrollo = None
desarrollo_final = None
equipo_venta = None
asesor_id = None

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


id_final_stage_a_equipo_venta = {
    #('2','3','4') : "equipo_asignacion"
    '7': "alfredo_vazquez",
    '8': 'ernesto_morales',
    '9': 'cesar_pelayo',
}

equipo_venta_sus_asesores = {
    "alfredo_vazquez": ["14754983", "14701776"],
    "ernesto_morales": ["14754983", "14701776"],
    "cesar_pelayo": ["14754983", "14701776"],
}

# Archivo para almacenar el registro de asignaciones
archivo_registro = 'api_integracion/registro_asignaciones.json'

def asignacion_automatica_asesores():
    global equipo_venta, asesor_id

    if equipo_venta is not None:
        # Cargar el registro de asignaciones desde el archivo
        registro_asignaciones = {}
        try:
            with open(archivo_registro, 'r') as file:
                registro_asignaciones = json.load(file)
        except FileNotFoundError:
            pass

        # Obtener el índice actual de asignación para el equipo actual
        indice_actual = registro_asignaciones.get(equipo_venta, 0)

        # Obtener los asesores disponibles en el equipo de venta
        asesores_disponibles = equipo_venta_sus_asesores.get(equipo_venta, [])

        # Calcular el índice de asesor a asignar
        indice_asignar = indice_actual % len(asesores_disponibles)
        asesor_asignado = asesores_disponibles[indice_asignar]
        print(f"Sumando 1 al índice de asignación para el equipo {equipo_venta}")

        # Actualizar el índice de asignación para el equipo actual
        registro_asignaciones[equipo_venta] = (indice_actual + 1) % len(asesores_disponibles)

        # Guardar el diccionario actualizado en el archivo
        with open(archivo_registro, 'w') as file:
            print(f"el indice actual:", indice_actual)
            json.dump(registro_asignaciones, file)
            print("Diccionario guardado correctamente:", registro_asignaciones)

        asesor_id = asesor_asignado  # Asignar el asesor seleccionado a asesor_id
        print(f"Se asignó el asesor {asesor_asignado}")
    else:
        print("No hay equipo de venta definido")

      
def agregar_persona(person_name, whatsapp_number):
  global person_id, id_deal

  if person_name is not None and whatsapp_number is not None:

      url_new_person = f"https://api.pipedrive.com/v1/persons?api_token={PIPEDRIVE_API_KEY}"

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
      url_new_deal = f"https://api.pipedrive.com/v1/deals?api_token={PIPEDRIVE_API_KEY}"

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
    url = f"https://api.pipedrive.com/v1/notes?api_token={PIPEDRIVE_API_KEY}"

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
    url_update_deal = f"https://api.pipedrive.com/v1/deals/{id_deal}?api_token={PIPEDRIVE_API_KEY}"
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
    url = f"https://api.pipedrive.com/v1/notes?api_token={PIPEDRIVE_API_KEY}"

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


def final_position_deal_cita (person_name, desarrollo_final, dia_cita, hora_cita, archivo_conversacion):
    global id_final_stage, asesor_id, equipo_venta
    id_final_stage = ruta_stage_a_id_final_stage.get(desarrollo_final)
    print(f"stage final asignado:",id_final_stage)
    
    if id_final_stage:
        equipo_venta = id_final_stage_a_equipo_venta.get(id_final_stage)
    else:
        # Manejo de error si el desarrollo_final no está en el diccionario ruta_stage_a_id_final_stage
        print("Desarrollo final no encontrado en el diccionario.")
    
    # Llamar a la función de asignación automática
    asignacion_automatica_asesores()

    print(f"equipo_venta:", equipo_venta)


    if id_deal is not None and id_final_stage is not None and asesor_id is not None:
      url_update_deal = f"https://api.pipedrive.com/v1/deals/{id_deal}?api_token={PIPEDRIVE_API_KEY}"
      print(f"link con deal:",url_update_deal)
    
      payload = json.dumps({
        "stage_id": id_final_stage,
        "user_id": asesor_id
      })
      print(f"stage final asignado:",id_final_stage)
      print(f"Asersor_venta:", asesor_id)

      headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Cookie': '__cf_bm=OnzSeI1FBndxoFILmn0Vobeoz71S9fp6E04Pnet8ChA-1692747443-0-AU6Ef3VBxrr9BSgWlDZQX0iIOOkPVkPaNfbxVhWrElbpYVwmnGBGCIPQPFdie4Dc2vNR08+DsEndH4TKDHmc5jI='
      }

      response = requests.request("PUT", url_update_deal, headers=headers, data=payload)

      #print(response.text)
      print(f"url_update_deal_si:", url_update_deal )
      print(f"id_final_stage_si:", id_final_stage )
    else:
      print("No se proporcionaron todos los datos ruta_stage")
      print(f"url_update_deal_no:", url_update_deal )
      print(f"id_final_stage_no:", id_final_stage )

    if id_final_stage is not None:
      url = f"https://api.pipedrive.com/v1/notes?api_token={PIPEDRIVE_API_KEY}"

      # Cargar el contenido de la conversación guardada
      with open(archivo_conversacion, 'r', encoding='utf-8') as archivo_entrada:
          conversacion_guardada = json.load(archivo_entrada)

      # Formatear el contenido de la conversación para incluirlo en la nota
      conversacion_formateada = "\n\n".join([f"{mensaje['remitente']}: {mensaje['mensaje']}" for mensaje in conversacion_guardada])

      # Dividir la conversación en notas más pequeñas si supera 1950 caracteres
      max_note_length = 7250
      conversacion_notas_divididas = [conversacion_formateada[i:i+max_note_length] for i in range(0, len(conversacion_formateada), max_note_length)]

      for i, nota in reversed(list(enumerate(conversacion_notas_divididas))):
          parte_nota = len(conversacion_notas_divididas) - i

          payload = json.dumps({
            "content": f"{person_name} ha pedido una cita el día: {dia_cita} a las: {hora_cita} \n\nConversación (Parte {parte_nota}):\n{nota}",
            "deal_id": id_deal
          })
          headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Cookie': '__cf_bm=VzMFgPKLCX96U7A_cmPGT3ughyFzbj7XxqoA5MblWQk-1692834913-0-AbpwgxOCFt38X4wmtw5k3PtcQ3vtiiapdHlqbjSdHGRCd5VKDdwKqjVQXgw++ROvMoPE6IXmxR5EnxsLnN1tdMk='
          }

          response = requests.request("POST", url, headers=headers, data=payload)
          with open(archivo_conversacion, 'w', encoding='utf-8') as archivo_salida:
              json.dump([], archivo_salida)

      #print(response.text)

def final_position_deal_asesor (person_name, desarrollo_final, archivo_conversacion):
    global id_final_stage, asesor_id, equipo_venta
    id_final_stage = ruta_stage_a_id_final_stage.get(desarrollo_final)
    print(f"stage final asignado:",id_final_stage)
    
    if id_final_stage:
        equipo_venta = id_final_stage_a_equipo_venta.get(id_final_stage)
    else:
        # Manejo de error si el desarrollo_final no está en el diccionario ruta_stage_a_id_final_stage
        print("Desarrollo final no encontrado en el diccionario.")
    
    # Llamar a la función de asignación automática
    asignacion_automatica_asesores()
    
    print(f"equipo_venta:", equipo_venta)

    if id_deal is not None and id_final_stage is not None and asesor_id is not None:
      url_update_deal = f"https://api.pipedrive.com/v1/deals/{id_deal}?api_token={PIPEDRIVE_API_KEY}"
      print(f"link con deal:",url_update_deal)
    
      payload = json.dumps({
        "stage_id": id_final_stage,
        "user_id": asesor_id
      })
      print(f"stage final asignado:",id_final_stage)
      print(f"asesor_ID:",asesor_id)
      headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Cookie': '__cf_bm=OnzSeI1FBndxoFILmn0Vobeoz71S9fp6E04Pnet8ChA-1692747443-0-AU6Ef3VBxrr9BSgWlDZQX0iIOOkPVkPaNfbxVhWrElbpYVwmnGBGCIPQPFdie4Dc2vNR08+DsEndH4TKDHmc5jI='
      }

      response = requests.request("PUT", url_update_deal, headers=headers, data=payload)

      #print(response.text)
      print(f"url_update_deal_si:", url_update_deal )
      print(f"id_final_stage_si:", id_final_stage )
    else:
      print("No se proporcionaron todos los datos ruta_stage")
      print(f"url_update_deal_no:", url_update_deal )
      print(f"id_final_stage_no:", id_final_stage )

    if id_final_stage is not None :
      url = f"https://api.pipedrive.com/v1/notes?api_token={PIPEDRIVE_API_KEY}"

      # Cargar el contenido de la conversación guardada
      with open(archivo_conversacion, 'r', encoding='utf-8') as archivo_entrada:
          conversacion_guardada = json.load(archivo_entrada)

      # Formatear el contenido de la conversación para incluirlo en la nota
      conversacion_formateada = "\n\n".join([f"{mensaje['remitente']}: {mensaje['mensaje']}" for mensaje in conversacion_guardada])

      # Dividir la conversación en notas más pequeñas si supera 1950 caracteres
      max_note_length = 7250
      conversacion_notas_divididas = [conversacion_formateada[i:i+max_note_length] for i in range(0, len(conversacion_formateada), max_note_length)]

      for i, nota in reversed(list(enumerate(conversacion_notas_divididas))):
          parte_nota = len(conversacion_notas_divididas) - i

          payload = json.dumps({
            "content": f"{person_name} ha pedido una asesoramiento sonbre {desarrollo_final} \n\nConversación (Parte {parte_nota}):\n{nota}",
            "deal_id": id_deal
          })
          headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Cookie': '__cf_bm=VzMFgPKLCX96U7A_cmPGT3ughyFzbj7XxqoA5MblWQk-1692834913-0-AbpwgxOCFt38X4wmtw5k3PtcQ3vtiiapdHlqbjSdHGRCd5VKDdwKqjVQXgw++ROvMoPE6IXmxR5EnxsLnN1tdMk='
          }

          response = requests.request("POST", url, headers=headers, data=payload)
          with open(archivo_conversacion, 'w', encoding='utf-8') as archivo_salida:
              json.dump([], archivo_salida)

      #print(response.text)

def final_position_deal_lead (person_name, desarrollo_final, archivo_conversacion):
  global id_final_stage
  id_final_stage = ruta_stage_a_id_final_stage.get(desarrollo_final)

  if id_deal is not None and id_final_stage is not None:
    url_update_deal = f"https://api.pipedrive.com/v1/deals/{id_deal}?api_token={PIPEDRIVE_API_KEY}"
    print(f"link con deal:",url_update_deal)
    payload = json.dumps({
      "stage_id": id_final_stage,
      "user_id": "14701776"
    })
    headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Cookie': '__cf_bm=OnzSeI1FBndxoFILmn0Vobeoz71S9fp6E04Pnet8ChA-1692747443-0-AU6Ef3VBxrr9BSgWlDZQX0iIOOkPVkPaNfbxVhWrElbpYVwmnGBGCIPQPFdie4Dc2vNR08+DsEndH4TKDHmc5jI='
    }

    response = requests.request("PUT", url_update_deal, headers=headers, data=payload, )

    #print(response.text)
    print(f"url_update_deal_si:", url_update_deal )
    print(f"id_first_stage_si:", id_first_stage )
  else:
    print("No se proporcionaron todos los datos ruta_stage")
    print(f"url_update_deal_no:", url_update_deal )
    print(f"id_first_stage_no:", id_first_stage )

  if id_final_stage is not None :
    url = f"https://api.pipedrive.com/v1/notes?api_token={PIPEDRIVE_API_KEY}"

    # Cargar el contenido de la conversación guardada
    with open(archivo_conversacion, 'r', encoding='utf-8') as archivo_entrada:
        conversacion_guardada = json.load(archivo_entrada)

    # Formatear el contenido de la conversación para incluirlo en la nota
    conversacion_formateada = "\n\n".join([f"{mensaje['remitente']}: {mensaje['mensaje']}" for mensaje in conversacion_guardada])

    # Dividir la conversación en notas más pequeñas si supera 1950 caracteres
    max_note_length = 7250
    conversacion_notas_divididas = [conversacion_formateada[i:i+max_note_length] for i in range(0, len(conversacion_formateada), max_note_length)]

    for i, nota in reversed(list(enumerate(conversacion_notas_divididas))):
        parte_nota = len(conversacion_notas_divididas) - i

        payload = json.dumps({
          "content": f"El bot no pudo ayudar a {person_name}, sobre el desarrollo: {desarrollo_final}\n\nConversación (Parte {parte_nota}):\n{nota}",
          "deal_id": id_deal
        })
        headers = {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
          'Cookie': '__cf_bm=VzMFgPKLCX96U7A_cmPGT3ughyFzbj7XxqoA5MblWQk-1692834913-0-AbpwgxOCFt38X4wmtw5k3PtcQ3vtiiapdHlqbjSdHGRCd5VKDdwKqjVQXgw++ROvMoPE6IXmxR5EnxsLnN1tdMk='
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        with open(archivo_conversacion, 'w', encoding='utf-8') as archivo_salida:
            json.dump([], archivo_salida)

    print(response.text)