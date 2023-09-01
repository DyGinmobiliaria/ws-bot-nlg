from config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER, OPENAI_API_KEY
from flask import Flask, request
from twilio.rest import Client
import openai
import spacy
from dotenv import load_dotenv
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.stem import WordNetLemmatizer
from emoji import assign_emojis
from datos_desarrollos import obtener_contexto
from faq_desarrollos import faq_DyG
from property_data import property_data
from phone_utils import process_phone_number
from zapier_utils import send_to_zapier
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
import nltk.data
from flask import Flask, request, jsonify
import random
from spacy.lang.es.stop_words import STOP_WORDS
from solicitudes_nombre import formas_solicitud_nombre
from saludos import obtener_saludo
import random
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
import datos_desarrollos
import json
import re
import urllib.parse
from word2number import w2n
from buscar_desarrollo import buscar_desarrollo, obtener_info_desarrollos_coincidentes
from unidecode import unidecode
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime, timedelta
import datetime
from unidecode import unidecode  # Importa la función unidecode
from difflib import get_close_matches
from numeros_en_espanol import numeros_en_espanol, numeros_en_espanol_pequenos
from api_integracion import pipe_add_person
from historial_conversacion import cargar_conversacion_desde_archivo, guardar_conversacion_en_archivo
from nltk.metrics import jaccard_distance
from nltk.corpus import wordnet
from difflib import get_close_matches
from fuzzywuzzy import fuzz
import unicodedata
from buscar_desarrollo import buscar_por_lugares_referencia
import threading
import time
import os
import sys
# Importar las funciones del controlador de conversaciones


load_dotenv()

# Crear la aplicación Flask
app = Flask(__name__)
archivo_conversacion = 'historial_conversacion.json'

historial_conversacion = cargar_conversacion_desde_archivo(archivo_conversacion)
historial_conversacion = []

# Cargar el modelo de spaCy para NER en español fuera de la función
nlp_model = spacy.load('es_core_news_lg')
# Definir variables y configuraciones
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
sia = SentimentIntensityAnalyzer()
lemmatizer = WordNetLemmatizer()

desarrollos = datos_desarrollos.desarrollos


"""def reiniciar_servidor():
    python = sys.executable
    os.execl(python, python, *sys.argv)

# Variable para controlar el contador de tiempo
contador_activo = False"""

# Función para el contador de tiempo
def contador_tiempo():
    global contador_activo

    contador_activo = True
    time.sleep(300)  # Espera durante 30 segundos
    if contador_activo:
        cerrar_conversacion(numero_telefono)
    contador_activo = False


def cargar_conversacion_desde_archivo(nombre_archivo):
    try:
        with open(nombre_archivo, 'r') as archivo:
            conversacion = json.load(archivo)
            return conversacion
    except FileNotFoundError:
        # Si el archivo no existe, se retorna una lista vacía
        return []
    except json.JSONDecodeError:
        # Si hay un error al decodificar el JSON, se retorna una lista vacía
        return []


def obtener_timestamp_actual():
    timestamp_actual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return timestamp_actual

def obtener_mensaje_del_usuario():
    # Aquí deberías tener la lógica para obtener el mensaje del usuario, por ejemplo:
    mensaje = input("Ingresa tu mensaje: ")  # Esto es solo un ejemplo, reemplázalo con tu lógica real
    return mensaje

def extract_entities(message, nlp_model):
    # Procesar el mensaje con el modelo de spaCy pasado como parámetro
    doc = nlp_model(message)

    # Obtener las entidades nombradas detalladas del mensaje
    named_entities = []
    for ent in doc.ents:
        named_entities.append({
            'text': ent.text,
            'start': ent.start_char,
            'end': ent.end_char,
            'label': ent.label_,
            'lemma': ent.lemma_
        })
    return named_entities

def preprocesar_mensaje(message):
    tokens = word_tokenize(message)
    pos_tags = pos_tag(tokens)
    return pos_tags


def extract_message_data(message, nlp_model):
    names = []

    # Aplicar el modelo de spaCy al mensaje utilizando el modelo pasado como parámetro
    doc = nlp_model(message)

    # Extraer las entidades nombradas relevantes del documento
    for entity in doc.ents:
        if entity.label_ in ["PER", "PERS", "ORG"]:
            names.append(entity.text)

    return names

# Función para detectar palabras clave en un mensaje
def detect_keywords(message, nlp_model):
    # Preprocesamiento adicional si es necesario (por ejemplo, eliminación de stopwords)

    # Tokenizar el mensaje
    doc = nlp_model(message)

    # Obtener las palabras clave (sustantivos, adjetivos, verbos, nombres propios, etc.)
    keywords = [token.lemma_ for token in doc if token.pos_ in ['NOUN', 'ADJ']]

    return keywords

# Función para verificar si un nombre de desarrollo es válido
def nombre_desarrollo_valido(nombre):
    for desarrollo in desarrollos:
        if isinstance(desarrollo['nombre'], list):
            if any(variante.lower() == nombre.lower() for variante in desarrollo['nombre']):
                return True
        else:
            if nombre.lower() == desarrollo['nombre'].lower():
                return True
    return False
# Función para verificar si un mensaje contiene un saludo junto con el nombre de un desarrollo
def mensaje_es_saludo_con_desarrollo(message):
    saludos = ['hola', 'buenos días', 'buenas tardes', 'buenas noches']
    for saludo in saludos:
        if saludo in message.lower():
            for desarrollo in desarrollos:
                if desarrollo['nombre'].lower() in message.lower():
                    return True
    return False

# Función para obtener el desarrollo de interés mencionado en un mensaje
def obtener_desarrollo_interesado(message):
    for desarrollo in desarrollos:
        if any(variante.lower() in message.lower() for variante in desarrollo['nombre']):
            return desarrollo

    return None

# Función para verificar si un mensaje menciona información del cliente
def menciona_informacion_cliente(message):
    # Utilizar expresiones regulares para detectar nombres
    # Aquí se asume que los nombres se componen de palabras que comienzan con una letra mayúscula
    pattern = re.compile(r'\b[A-Z][a-z]*\b')
    matches = pattern.findall(message)
    return len(matches) > 0


# Función para obtener la faq correspondiente a un desarrollo de interés
def obtener_faq_desarrollo(desarrollo_interesado):
    for desarrollo in desarrollos:
        if desarrollo['nombre'] == desarrollo_interesado:
            return desarrollo['nombre']

    return None

def detectar_intenciones(pos_tags, message):
    # Realizar análisis de sentimiento
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(message)
    sentiment_score = sentiment_scores['compound']

    
    # Realizar análisis de entidades nombradas
    doc = nlp_model(message)
    named_entities = [ent.text for ent in doc.ents]

    # Determinar la intención del cliente
    intencion = None  # Asignar un valor predeterminado a la variable intencion

    if sentiment_score <= -0.05:
        intencion = 'queja'
    else:
        message = message.lower()
        
        # Detectar intención de Compra o Adquisición
        palabras_clave_compra = ["comprar", "adquirir", "cotización", "precio", "disponibilidad"]
        if any(palabra in message for palabra in palabras_clave_compra):
            intencion = 'compra'

        # Detectar intención de Solicitar Información Adicional
        palabras_clave_info = ["dime más sobre", "necesito detalles de", "explícame acerca de"]
        if any(palabra in message for palabra in palabras_clave_info):
            intencion = 'informacion_adicional'

        # Detectar intención de Solicitar Asesoría o Ayuda
        palabras_clave_asesoria = ["ayuda", "asesoría", "dudas", "consultoría", "asesor"]
        if any(palabra in message for palabra in palabras_clave_asesoria):
            intencion = 'asesoria'

        # Detectar intención de Agendar una Cita o Visita
        palabras_clave_cita = ["cita", "visita", "concretar una reunión", "agenda"]
        
        if any(palabra in message for palabra in palabras_clave_cita):
            intencion = 'agendar_cita'

        # Detectar intención de Expresión de Interés en un Producto o Servicio
        palabras_clave_interes = ["me encanata", "es perfecto"]
        if any(palabra in message for palabra in palabras_clave_interes) and sentiment_score > 0.05 and not intencion:
            intencion = 'interes_producto'

        # Detectar intención de Agradecimiento o Satisfacción
        palabras_clave_agradecimiento = [ "excelente servicio", "adiós", "Hasta luego", "nos vemos", "hasta pronto", "que te vaya bien", "cuídate", "te veo después", "chao", "hasta la próxima", "nos vemos despues", "hasta mañana", "hasta pronto", "adiós", "bye"]
        if any(palabra in message for palabra in palabras_clave_agradecimiento):
            intencion = 'agradecimiento'
        
        # Detectar intención de Expresión de Desinterés
        palabras_clave_desinteres = ["no me gustó", "no me interesó", "no tengo", "sin interés", "otro proyecto", "que me puedes decir de", "otro desarrollo", "desarrollo cerca"]
        if any(palabra in message for palabra in palabras_clave_desinteres):
            intencion = 'desinteres'
        
        # Detectar intención de Expresión de Desinterés
        palabras_clave_desinteres = ["DyG", "DYG", "diseño y gestión", "inmobiliaria ", "desarrolladora", "quienes son", "diseño y gestion", "dyg", ]
        if any(palabra in message for palabra in palabras_clave_desinteres):
            intencion = 'diseno_gestion'

        # Detectar intención de Expresión de Desinterés
        palabras_clave_desinteres = ["ubicado", "ubicación", "donde estan", "donde se encuentran", "dirección"]
        if any(palabra in message for palabra in palabras_clave_desinteres):
            intencion = 'diseno_gestion_ubicacion'

        # Detectar intención de Expresión de Desinterés
        palabras_clave_proveedor = ["proveedores", "proveedor", "socio comercial", "fabricante", "mayorista", "suministro", "numero de compras", "inmobiliaria", "inmobiliario" ]
        if any(palabra in message for palabra in palabras_clave_proveedor):
            intencion = 'proveedor'
            print(f"ponemos en intension: Proveedor")
       
    return intencion

def generar_respuesta(intencion, ultimo_mensaje_cliente):

    if intencion == 'queja':
        mensaje_cliente_encoded = urllib.parse.quote(ultimo_mensaje_cliente)
        texto_resaltado = "*Reclamo abierto:*"
        texto_resaltado_encoded = urllib.parse.quote(texto_resaltado)
        enlace_botón = f"https://api.whatsapp.com/send?phone=+523310678076&text={texto_resaltado_encoded}%0A{mensaje_cliente_encoded}"
        respuesta = f"Lamentamos escuchar eso. Por favor, envíanos los detalles de tu queja y nos pondremos en contacto contigo lo antes posible. Puedes hacer clic en el siguiente enlace para abrir WhatsApp y contactar al departamento de Calidad.\n\n{texto_resaltado}\n{enlace_botón}"
        return respuesta  
    
def diseno_gestion(intencion):

    if intencion == 'diseno_gestion':
        respuesta = f"*Diseño y Gestión Inmobiliaria expertos en vivienda vertical 25 años marcando diferencia en el sector inmobiliario*\n\n Desarrolladora con un portafolio de más de 3,800 viviendas construidas, dedicada a la construcción de obra civil, tanto pública como privada, especializada en proyectos de vivienda vertical."
        return respuesta 
    
    if intencion == 'diseno_gestion_ubicacion':
        respuesta = f"puedes encontrar toda la informacón de *diseño y gestión inmobiliaria* \n\nhttps://disenoygestion.mx/"
        return respuesta 
    
# Función para normalizar una cadena de texto
def normalize_string(text):
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8').lower()

# Función para buscar una respuesta en el archivo JSON
def buscar_respuesta(ruta_archivo, pregunta):
    pregunta_normalizada = normalize_string(pregunta)
    mejor_coincidencia = None
    max_similitud = 0
    min_similitud = 70

    with open(ruta_archivo, 'r') as json_file:
        contenido = json.load(json_file)

        for faq in contenido:
            for preg in faq["preguntas"]:
                similitud = fuzz.ratio(pregunta_normalizada, normalize_string(preg))
                if similitud >= min_similitud and similitud > max_similitud:
                    max_similitud = similitud
                    mejor_coincidencia = preg

        if mejor_coincidencia:
            for faq in contenido:
                if mejor_coincidencia in faq["preguntas"]:
                    return faq["respuesta"], faq.get("link_multimedia"),

    return None, None

def obtener_presupuesto(texto):
    # Buscar cualquier secuencia de dígitos que pueda contener comas para separar miles
    match = re.search(r'\$?\d{1,3}(?:,\d{3})*(?:\.\d+)?', texto)
    if match:
        presupuesto = match.group().replace('$', '').replace(',', '')
        try:
            valor_presupuesto = float(presupuesto)
            if valor_presupuesto >= 100000:
                return valor_presupuesto
        except ValueError:
            pass
    return None


dia_cita = None
hora_cita = None

dia_en_es = {
    'monday': 'lunes',
    'tuesday': 'martes',
    'wednesday': 'miércoles',
    'thursday': 'jueves',
    'friday': 'viernes',
    'saturday': 'sábado',
    'sunday': 'domingo'
}

def obtener_dia_hora_cita(message):
    global dia_cita, hora_cita

    doc = nlp_model(message)

    dias_semana = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo", "miercoles", "sabado"]
    horas_positivas = ["am", "pm"]
    horas_keywords = ["mañana", "tarde", "noche"]
    dias_keywords = ["hoy", "mañana", "pasado mañana", "fin de semana"]
    date_time = datetime.datetime

    for ent in doc.ents:
        if ent.label_ == "DATE":
            dia_cita_en = ent.text
            if dia_cita_en:
                if dia_cita_en.lower() in dia_en_es:
                    dia_cita = dia_en_es[dia_cita_en.lower()]  # Traducir el día a español si está en el diccionario
        elif ent.label_ == "TIME":
            hora_tokens = ent.text.split()
            if len(hora_tokens) == 2 and hora_tokens[1].lower() in horas_positivas:
                hora_cita = ent.text
            elif any(keyword in ent.text.lower() for keyword in horas_keywords):
                hora_cita = ent.text

    for keyword in dias_keywords:
        if keyword in message.lower():
            if keyword == "hoy":
                dia_cita_en = date_time.now().strftime("%A")
            elif keyword == "mañana":
                dia_cita_en = (date_time.now() + timedelta(days=1)).strftime("%A")
            elif keyword == "pasado mañana":
                dia_cita_en = (date_time.now() + timedelta(days=2)).strftime("%A")
            elif keyword == "fin de semana":
                dia_cita_en = "sábado" if datetime.now().weekday() < 5 else "domingo"


            if dia_cita_en.lower() in dia_en_es:
                dia_cita = dia_en_es[dia_cita_en.lower()]  # Traducir el día a español si está en el diccionario
        # Diccionario de correspondencia entre abreviaturas y días de la semana
    correspondencia_dias = {
        "miercoles": "miércoles",
        "sabado": "sábado"
    }

    for keyword in dias_semana:
        if keyword in message.lower():
            # Usar directamente el día de la semana mencionado o su equivalente en el diccionario
            dia_cita = correspondencia_dias.get(keyword, keyword)

    # Buscar patrones de hora en diferentes formatos
    hora_patterns = [
        r'\d{1,2}:\d{2}\s?(am|pm)?',
        r'\d{1,2}:(am|pm)?',
        r'\d{1,2}:\d{2}?',
        r'\d{1,2}',
    ]
    for pattern in hora_patterns:
        hora_match = re.search(pattern, message)
        if hora_match:
            hora_cita = hora_match.group()
            break  # Detenerse en el primer patrón coincidente encontrado

    return dia_cita, hora_cita

numeros_en_espanol_normalized = {unidecode(clave.lower()): valor for clave, valor in numeros_en_espanol.items()}
 
def verificar_similitud_presupuesto_en_mensaje(texto):
    texto = unidecode(texto.replace("$", "").replace(",", "")).lower()  # Normaliza el texto sin acentos
    numeros = numeros_en_espanol_normalized.keys()
    matches = []
    

    for numero in numeros:
        if numero in texto:
            matches.append(numero)

    if matches:
        match = max(matches, key=len)  # Escoge la coincidencia más larga
        presupuesto_encontrado = numeros_en_espanol_normalized[match]
        return presupuesto_encontrado

numeros_en_espanol_lower = {clave.lower(): valor for clave, valor in numeros_en_espanol.items()}

def verificar_presupuesto_en_mensaje(text):
    # Aplicar transformación al mensaje para eliminar símbolo de precios y comas
    text = text.replace("$", "").replace(",", "").lower()
    
    numeros = numeros_en_espanol_lower.keys()
    matches = get_close_matches(text, numeros, n=1, cutoff=0.8)
    
    if matches:
        match = matches[0]
        numero_obtenido = numeros_en_espanol_lower[match]
        print(f"Número obtenido del diccionario: {numero_obtenido}")
        return numero_obtenido
    
    # Obtener las palabras del mensaje
    palabras = text.split()

    # Verificar si alguna palabra del mensaje está en el diccionario y es mayor o igual a 100000
    presupuesto_encontrado = any(
        palabra in numeros_en_espanol_lower and numeros_en_espanol_lower[palabra] >= 100000
        for palabra in palabras
    )
    
    return presupuesto_encontrado

def obtener_numero(message):
    # Diccionario de números en español    
    numero = None
    palabras = message.split()
    
    # Intentar detectar número en formato numérico
    for palabra in palabras:
        palabra_sin_puntuacion = palabra.replace(",", "").replace(".", "")  # Remover puntuación
        if palabra_sin_puntuacion.isdigit():
            numero = int(palabra_sin_puntuacion)
            print(f"Número encontrado (formato numérico): {numero}")
            break  # Salir del bucle si se encuentra un número
    
    # Si no se encontró un número en formato numérico, buscar en el diccionario
    if numero is None:
        for palabra in palabras:
            palabra_lower = palabra.lower()
            if palabra_lower in numeros_en_espanol_pequenos:
                numero = numeros_en_espanol_pequenos[palabra_lower]
                print(f"Número encontrado (forma escrita): {numero} (palabra: {palabra})")
                break
    
    return numero

# Variables globales para almacenar la información del usuario
nombre_usuario = None
numero_telefono = None
contexto = None
ruta_archivo = None
ruta_archivo_temporal = ruta_archivo 
desarrollo_interesado = None
contexto_global = None
mucho_gusto = None
# Diccionario para relacionar la ruta del archivo con el desarrollo interesado
archivo_a_desarrollo = {
    'faq_desarrollos/faq_Sant_Maarten.json': 'Sant Maärten Lofts',
    'faq_desarrollos/faq_kartesia.json': 'Kartesia Residencial',
    'faq_desarrollos/faq_Maria_jose.json': 'María José Living',
    'faq_desarrollos/faq_Soneto.json': 'Soneto Residencial',
    # Agrega más elementos si tienes más archivos y desarrollos asociados
}

def guardar_informacion_usuario(nombre, telefono, archivo, desarrollo, contexto):
    global nombre_usuario, numero_telefono, ruta_archivo, desarrollo_interesado, contexto_global, mucho_gusto

    # Actualizar las variables globales solo si aún no tienen un valor asignado
    if nombre_usuario is None:
        nombre_usuario = nombre

    if numero_telefono is None:
        numero_telefono = telefono

    if ruta_archivo is None:
        ruta_archivo = archivo  # Solo establecer ruta_archivo si aún no tiene un valor

    if desarrollo_interesado is None:
        desarrollo_interesado = desarrollo

    if mucho_gusto is None:
        mucho_gusto = mucho_gusto

    # Siempre asignar un valor a contexto_global, independientemente de su valor actual
    contexto_global = contexto
    print(f"contexto global: {contexto_global}")
    print(f"Contexto: {contexto}")

    if desarrollo_interesado is not None:
        ruta_stage = ruta_archivo
        desarrollo = desarrollo_interesado
        print(f"ruta stage:",ruta_stage)
        pipe_add_person.update_deal(person_name, ruta_stage, desarrollo)
        print(f"El desarrollo interesado es: {desarrollo_interesado}")
    else:
        print("No se encontró desarrollo interesado para la ruta del archivo proporcionada.")


def cerrar_conversacion(formatted_phone_number):
    global nombre_usuario, numero_telefono, ruta_archivo, desarrollo_interesado, contexto_global, mucho_gusto

    # Aquí puedes agregar el código necesario para cerrar la conversación
    # Por ejemplo, podrías liberar recursos, cambiar el estado de la conversación, etc.
    # Asegúrate de manejar adecuadamente la conversación asociada al número de teléfono.
    despedida = "Muchas gracias por contactarte con *Diseño y Gestión Inmobilaria* esperamos verte pronto."
            
    send_whatsapp_message(formatted_phone_number, despedida)
    # Ejemplo: Reiniciar todas las variables a None
    nombre_usuario = None
    numero_telefono = None
    contexto = None
    ruta_archivo = None
    desarrollo_interesado = None
    contexto_global = None
    mucho_gusto = None
    historial_conversacion.clear()

    return "Conversación cerrada"

"""# En tu código principal
historial_conversacion = []"""
"""reiniciar_servidor()"""

@app.route('/whatsapp', methods=['POST'])
def process_message():
    global nombre_usuario, desarrollo_interesado, ruta_archivo, mucho_gusto, whatsapp_number, person_name, ruta_stage, numero_telefono
    # Obtener el mensaje y el número de teléfono del remitente
    message = request.form.get('Body')
    formatted_phone_number = ''
    phone_number_string = request.form.get('From')

    # Procesar número de teléfono
    formatted_phone_number = process_phone_number(phone_number_string)
    numero_telefono = formatted_phone_number
    print("formated_number:",formatted_phone_number)
    """ if contador_activo:
        contador_activo = False
        contador_thread.join()

        contador_thread = threading.Thread(target=contador_tiempo)
        contador_thread.start()"""

    print("Mensaje enviado:", message)
    mensaje_recibido = request.form['Body']  # Esto es un ejemplo, reemplázalo con tu lógica
    print("mensaje_recibido:", mensaje_recibido)
    nuevo_mensaje = {
        "remitente": nombre_usuario,
        "mensaje": mensaje_recibido, 
        "timestamp": obtener_timestamp_actual()   # Asegúrate de tener una función para obtener la hora actual
    }
    historial_conversacion.append(nuevo_mensaje)
    guardar_conversacion_en_archivo(historial_conversacion, archivo_conversacion)
    print("Mensaje agregado al historial:", nuevo_mensaje)

    pos_tags = pos_tag(word_tokenize(message))
    if detectar_intenciones(pos_tags, message) == 'proveedor':

       # respuesta = mandar_proveedor(detectar_intenciones(pos_tags, message))
        #send_whatsapp_message(formatted_phone_number, respuesta)
        return "OK"
    
    pos_tags = pos_tag(word_tokenize(message))
    if detectar_intenciones(pos_tags, message) == 'diseno_gestion':
        respuesta = diseno_gestion(detectar_intenciones(pos_tags, message))
        send_whatsapp_message(formatted_phone_number, respuesta)
        return "OK"

    
    if nombre_usuario is not None and ruta_archivo is not None:
        # Llamar directamente a la función buscar_sentimientos
        respuesta = buscar_sentimientos(ruta_archivo, message, formatted_phone_number)
        
        return "OK"
    pos_tags = pos_tag(word_tokenize(message))
    if detectar_intenciones(pos_tags, message) == 'diseno_gestion_ubicacion':
        respuesta = diseno_gestion(detectar_intenciones(pos_tags, message))
        send_whatsapp_message(formatted_phone_number, respuesta)
        return "OK"


    # Verificar si el mensaje contiene una queja
    pos_tags = pos_tag(word_tokenize(message))
    if detectar_intenciones(pos_tags, message) == 'queja':
        respuesta = generar_respuesta('queja', message)  # Generar una respuesta correspondiente a la queja
        send_whatsapp_message(formatted_phone_number, respuesta)
        return "OK"

    # Continuar con el proceso si no es una queja

    if menciona_informacion_cliente(message):
        nombres_entidades = extract_message_data(message, nlp_model)  # Pasar el modelo de spaCy como argumento

        # Filtrar los nombres de entidades que no sean similares a nombres o modelos de desarrollos
        nombres_filtrados = []
        for nombre in nombres_entidades:
            if not nombre_desarrollo_valido(nombre):
                nombres_filtrados.append(nombre)
    # Si ya se tiene la ruta de archivo, no es necesario llamar a obtener_contexto
            # Almacenar el nombre del cliente solo si no ha sido obtenido previamente
        if nombre_usuario is None:
            nombre_usuario = nombres_filtrados[0] if nombres_filtrados else None
                # Si ya tenemos el nombre del usuario, pero no el desarrollo de interés, preguntamos por el desarrollo

    # Obtener el saludo según la hora actual
    saludo = obtener_saludo()
    if ruta_archivo is None:
        # Obtener el contexto solo si no se tiene ya la ruta de archivo
        contexto, ruta_archivo = obtener_contexto(message)
        desarrollo_interesado = archivo_a_desarrollo.get(ruta_archivo)
        ruta_archivo_temporal = ruta_archivo
        guardar_informacion_usuario(nombre_usuario, numero_telefono, ruta_archivo_temporal, desarrollo_interesado, contexto)

    if ruta_archivo is not None and nombre_usuario is not None:
          # Imprimir la ruta del archivo recibida como argumento
        # Cerrar el ciclo actual y solicitar más información si es necesario
        mensaje_saludo = f"*{nombre_usuario}* {contexto_global}"
        send_whatsapp_message(formatted_phone_number, mensaje_saludo)
        send_whatsapp_message(formatted_phone_number, f"¿Qué te gustaría conocer más de *{desarrollo_interesado}*? ¿Sus amenidades o modelos disponibles?")
        return "OK" 
    
    # Detección de palabras clave y extracción de entidades
    keywords = detect_keywords(message, nlp_model)  # Pasar el modelo de spaCy como argumento
    entities = extract_entities(message, nlp_model)  # Pasar el modelo de spaCy como argumento
    names = extract_message_data(message, nlp_model)  # Pasar el modelo de spaCy como argumento

    # Si ya se tiene el desarrollo interesado, no se sobrescribe

    if ruta_archivo is not None and nombre_usuario is not None:
        # Caso 1: El cliente menciona su nombre y el proyecto interesado
        mensaje_saludo = f"{saludo} {nombre_usuario}! {contexto}"
        send_whatsapp_message(formatted_phone_number, mensaje_saludo)
        send_whatsapp_message(formatted_phone_number, f"¿Qué te gustaría conocer más de *{desarrollo_interesado}*? ¿Sus amenidades o modelos disponibles?")
        return "OK"

    if ruta_archivo is not None and nombre_usuario is None:
        # Caso 2: El cliente menciona solo el proyecto interesado, pero no proporciona su nombre
        mensaje_saludo = f"{saludo}!👋🏻 Gracias por contactarnos y por tu interés en nuestro desarrollo *{desarrollo_interesado}*."
        send_whatsapp_message(formatted_phone_number, mensaje_saludo)
        solicitud_nombre = random.choice(formas_solicitud_nombre)
        send_whatsapp_message(formatted_phone_number, solicitud_nombre)
        return "OK"
        # Si ya tenemos el nombre del usuario, pero no el desarrollo de interés, preguntamos por el desarrollo


    if nombre_usuario is not None and ruta_archivo is None and mucho_gusto is None:
            send_whatsapp_message(formatted_phone_number, f"Mucho gusto *{nombre_usuario}* 🌟 ¿De qué desarrollo te gustaría recibir información? 🏢  \n\nSi no conoces el nombre del desarrollo, puedes preguntarme por📍ubicaciones cercanas o 💰rangos de precio.")
            mucho_gusto = True
            message = "no_action"  # Establecer message como cadena vacía
            whatsapp_number = numero_telefono
            person_name = nombre_usuario
            pipe_add_person.agregar_persona(person_name, whatsapp_number)

    if nombre_usuario is not None and ruta_archivo is None and mucho_gusto is True: 
            
            doc = nlp_model(message)
            print(f"mensaje del usario:",message)
            #print(f"Resultado del análisis del modelo de lenguaje: {doc}")
            entidades_nombradas = extract_entities(message, nlp_model)

            tokens_importantes = detect_keywords(message, nlp_model)
            # Aplicar transformación al mensaje para eliminar símbolo de precios y comas
            message = message.replace("$", "").replace(",", "").lower()

            ubicacion = None
            presupuesto = None
            recamaras = None
            banos = None
            estacionamientos = None
            print(f"presupuesto que llega a la variable:", presupuesto)

            if message :
                presupuesto = verificar_presupuesto_en_mensaje(message)
                print(f"Tiene presupuesto mayor o igual a 100000 1: {presupuesto}")
                print(f"presupuesto que llega a la variable if message:", presupuesto)
             
                if message.isdigit():
                    presupuesto = int(message)
                    print(f"Presupuesto encontrado: {presupuesto}")
                    print(f"presupuesto que llega a la variable:", presupuesto)
                
            # Agregar las palabras clave como entidades nombradas
            for keyword in tokens_importantes:
                entidades_nombradas.append({'text': keyword, 'start': -1, 'end': -1, 'label': 'KEYWORD', 'lemma': keyword})
                
                #ent_text_lower = ent['text'].lower()  # Convertir el texto de la entidad a minúsculas

            else:
                for ent in entidades_nombradas:
                    #print(f"Resultado del análisis del modelo de lenguaje: {ent['text']}")
                    #print(f"Entidades nombradas: {entidades_nombradas}")
                    
                    if any(word in ent['text'].lower().split() for word in ['baños', 'baño', 'bano']):
                        banos = obtener_numero(message)
                        #banos = obtener_numero(ent['text'])

                        #print(f"Texto de entidad: {ent['text']}")  # Agregar esta línea para mostrar el texto de la entidad
                        print(f"Encontrado 'baños': {banos}")
                    elif any(word in ent['text'].lower().split() for word in ['recámaras', 'recámara', 'habitaciones', 'habitación', 'recamara', 'recamaras']):
                        recamaras = obtener_numero(message)
                        #recamaras = obtener_numero(ent['text'])

                        #print(f"Texto de entidad: {ent['text']}")  # Agregar esta línea para mostrar el texto de la entidad
                        print(f"Encontrado 'recámaras': {recamaras}")

                    elif any(word in ent['text'].lower().split() for word in ['estacionamientos', 'estacionamiento']):
                        estacionamientos = obtener_numero(message)
                        #estacionamientos = obtener_numero(ent['text'])
                       # print(f"Texto de entidad: {ent['text']}")  # Agregar esta línea para mostrar el texto de la entidad
                        print(f"Encontrado 'estacionamientos': {estacionamientos}")

                    
                    elif any(word in ent['text'].lower().split() for word in ['presupuesto', 'tengo']):
                        presupuesto_verificado = verificar_similitud_presupuesto_en_mensaje(message)
                        presupuesto = obtener_numero(message)
                        
                        if presupuesto_verificado:
                            presupuesto = presupuesto_verificado
                            print(f"Texto de entidad: {ent['text']}")
                            print(f"Presupuesto verificado encontrado: {presupuesto_verificado}")
                        
                            if presupuesto:
                                print(f"Texto de entidad: {ent['text']}")
                                print(f"Presupuesto numérico encontrado: {presupuesto}")

                else:
                    if message:
                        ubicaciones = message.split()  # Dividir el mensaje en una lista de ubicaciones
                        resultados_totales = []  # Inicializar una lista para almacenar los resultados totales

                        # Convertir cada ubicación en minúsculas y buscar por lugares de referencia
                        for ubicacion in ubicaciones:
                            resultados_por_ubicacion = buscar_por_lugares_referencia(ubicacion.lower())
                            resultados_totales.extend(resultados_por_ubicacion)

             #       elif ent['label']:
             #           ubicacion = ent['text']

                resultados_coincidentes = buscar_desarrollo(ubicacion, presupuesto, recamaras, banos, estacionamientos)

            if message == "no_action": # Comprueba si message no está vacío después de eliminar espacios en blanco
                pass
            else:
                if resultados_coincidentes:
                    formatted_results = obtener_info_desarrollos_coincidentes(resultados_coincidentes)

                    message1 = f"Con mucho gusto *{nombre_usuario}*, encontré los siguientes desarrollos que podrían interesarte:\n\n{formatted_results}"
                    send_whatsapp_message(formatted_phone_number, message1)

                    message2 = "Si te gustaría recibir más información de alguno, escribe el nombre y te brindaré información más detallada.😁"
                    send_whatsapp_message(formatted_phone_number, message2)
                        # Verificar si message está vacío antes de enviar el mensaje "Lo siento, no encontré desarrollos que coincidan con tu búsqueda."
                else:
                    send_whatsapp_message(formatted_phone_number, "Lo siento, no encontré desarrollos que coincidan con tu búsqueda.")

            return "OK"
                    
    if nombre_usuario is not None and ruta_archivo is not None:
        print(f"ruta archivo_update",ruta_archivo)
        respuesta = buscar_sentimientos (ruta_archivo, message, formatted_phone_number)

        print(f"Ruta del archivo recibida 1: {ruta_archivo}")  # Imprimir la ruta del archivo recibida como argumento
        # Cerrar el ciclo actual y solicitar más información si es necesario
        mensaje_saludo = f"{saludo} {nombre_usuario}! {contexto}"
        send_whatsapp_message(formatted_phone_number, mensaje_saludo)
        send_whatsapp_message(formatted_phone_number, f"¿Qué te gustaría conocer más de *{desarrollo_interesado}*? ¿Sus amenidades o modelos disponibles?")
        return "OK"          

    solicitud_nombre = random.choice(formas_solicitud_nombre)
    mensaje_saludo = f"{obtener_saludo()}! 👋🏻¡Gracias por comunicarte a Diseño y Gestión Inmobiliaria *expertos en vivienda vertical* 🏗️🏙️ {solicitud_nombre} \n\n¿Eres proveedor o prestador de servicios? Envía tu información al correo 👉📨 : compras@disenoygestion.mx"
    send_whatsapp_message(formatted_phone_number, mensaje_saludo)

    print(f"ruta archivo: {ruta_archivo}")
    print(f"Desarrollo interesado: {desarrollo_interesado}")
    print(f"nombre:  {nombre_usuario}")
    return "OK"

# Definir una variable para almacenar el sentimiento globalmente
sentimiento_global = None
print(f"sentimiento global:",sentimiento_global)


def buscar_sentimientos(ruta_archivo, message, formatted_phone_number):
    global sentimiento_global  # Declarar que se utilizará la variable global
    pos_tags = pos_tag(word_tokenize(message))
    intencion = detectar_intenciones(pos_tags, message)
    print ("sentimiento_global=",sentimiento_global)


contador_respuestas_contestar_faqs = 0  # Contador para llevar el registro de las respuestas de contestar_faqs
max_respuestas_contestar_faqs = 3 # Número máximo de respuestas consecutivas de contestar_faqs
contador_mediumrespuestas_contestar_faqs = 0
mediumrespuestas_contestar_faqs = 3 # Número medio de respuestas consecutivas de contestar_faqs

contador_no_respuestas_faqs = 0  # Contador para llevar el registro de las respuestas no encontradas en faqs
max_contador_no_respuestas_faqs = 3  # Número máximo de respuestas no encontradas en faqs


def contestar_faqs(ruta_archivo, message, formatted_phone_number):
    global contador_respuestas_contestar_faqs, contador_no_respuestas_faqs, contador_mediumrespuestas_contestar_faqs
    
    # Imprimir valores actuales de los contadores
    print("Valor actual de contador_respuestas_contestar_faqs:", contador_respuestas_contestar_faqs)
    print("Valor actual de contador_mediumrespuestas_contestar_faqs:", contador_mediumrespuestas_contestar_faqs)
    print("Valor actual de contador_no_respuestas_faqs:", contador_no_respuestas_faqs)

    # Abrir el archivo JSON correspondiente usando la ruta almacenada en 'ruta_archivo'
    with open(ruta_archivo, 'r') as file:
        contenido = file.read()

        # Cargar el contenido como una lista de diccionarios utilizando json.loads()
        preguntas_respuestas = json.loads(contenido)

        # Buscar respuesta en FAQs
        respuesta, links_multimedia = buscar_respuesta(ruta_archivo, message)
        
        # Definir las entidades nombradas y tokens importantes del mensaje
        entidades_nombradas = extract_entities(message, nlp_model)
        tokens_importantes = detect_keywords(message, nlp_model)

        # Convertir el mensaje y las preguntas a minúsculas
        message = message.lower()
        preguntas_respuestas_lower = [
            {'preguntas': [pregunta.lower() for pregunta in item['preguntas']], 'respuesta': item['respuesta']}
            for item in preguntas_respuestas
        ]

        respuesta_encontrada = None
        link_multimedia_encontrados = None  # Inicializar la variable

        # Buscar preguntas similares y obtener las respuestas correspondientes
        for item in preguntas_respuestas:
            preguntas = item['preguntas']
            respuestas = item['respuesta']

            # Verificar si alguna de las preguntas tiene entidades o tokens similares
            respuesta_encontrada, link_multimedia_encontrados, = buscar_respuesta(ruta_archivo, message)

            # Si la pregunta tiene entidades o tokens similares, guardar la respuesta
            if respuesta_encontrada:
                print("Respuesta encontrada:", respuesta_encontrada)

                # Verificar si hay un enlace multimedia asociado
                if 'link_multimedia' in item:
                    link_multimedia_encontrados = item['link_multimedia']
                    print("Enlaces multimedia encontrados:", link_multimedia_encontrados)

                #break

            if respuesta_encontrada:
                break

        if respuesta_encontrada:
            # Generar respuesta coherente con ChatGPT utilizando la respuesta encontrada
            send_whatsapp_message(formatted_phone_number, respuesta_encontrada)

            # Aumentar el contador de respuestas contestar_faqs
            contador_respuestas_contestar_faqs += 1
            contador_mediumrespuestas_contestar_faqs += 1
            print("Contadores incrementados")

            if contador_mediumrespuestas_contestar_faqs == mediumrespuestas_contestar_faqs:
                brochure_financiamiento = "También te puedo apoyar con el brochure o los métodos de financiamiento."
                send_whatsapp_message(formatted_phone_number, brochure_financiamiento)

            if contador_respuestas_contestar_faqs == max_respuestas_contestar_faqs:
                contador_respuestas_contestar_faqs = 0  # Reiniciar el contador
                contador_no_respuestas_faqs = 0
                contador_mediumrespuestas_contestar_faqs = 0  # Reiniciar el contador
                asesor_cita = f"*{nombre_usuario}* Veo que te gustaría recibir más información, ¿puedo comunicarte con un asesor o programarte una cita? 👨🏽‍💻"
                send_whatsapp_message(formatted_phone_number, asesor_cita)
                return asesor_cita
            
        if link_multimedia_encontrados:
            print("Enlaces multimedia encontrados:", link_multimedia_encontrados)
            send_whatsapp_multimedia(formatted_phone_number, media_urls=link_multimedia_encontrados)
        else:
            print("No se encontraron enlaces multimedia.")
            # La variable link_multimedia_encontrado no está definida, no hay enlace multimedia
            pass

        # Si no se encontró ninguna respuesta válida y no se encontró ningún enlace
        if respuesta_encontrada is None:
            no_respuesta = "Lo siento, no entendí la pregunta. ¿Cómo te puedo apoyar? ☺️"
            send_whatsapp_message(formatted_phone_number, no_respuesta)

            # Aumentar el contador de no respuestas en FAQs
            contador_no_respuestas_faqs += 1
            
            if contador_no_respuestas_faqs == max_contador_no_respuestas_faqs:
                contador_no_respuestas_faqs = 0  # Reiniciar el contador máximo
                
                desarrollo_final = desarrollo_interesado + "_lead"
                print(f"ruta stage:",desarrollo_final)
                pipe_add_person.final_position_deal_lead(person_name, desarrollo_final, archivo_conversacion)

                capacidad = f"*{nombre_usuario}* Creo que mi capacidad de respuesta llegó a su límite.💔 ¡No te preocupes! 😁 Un asesor te contactará en breve para darte seguimiento. 👨🏽‍💻"
                send_whatsapp_message(formatted_phone_number, capacidad)
                sentimiento_global = "mandar_prospeccion"  # Cambiar la variable global para activar preguntar_por_asesor
                return capacidad


def buscar_sentimientos(ruta_archivo, message, formatted_phone_number):
    global sentimiento_global
    pos_tags = pos_tag(word_tokenize(message))
    intencion = detectar_intenciones(pos_tags, message)

    if sentimiento_global == 'agradecimiento':
        agradecimiento = "Muchas gracias por contactarte con *Diseño y Gestión Inmobilaria* esperamos verte pronto."
        send_whatsapp_message(formatted_phone_number, agradecimiento)
        print("Estamos agradecidos")

    elif sentimiento_global in ['agendar_cita', 'interes_producto']:
        respuesta = agendar_cita(formatted_phone_number, message)
        print("Pasamos a preguntar asesor")

    elif sentimiento_global in ['compra', 'asesoria', 'informacion_adicional',]:
        respuesta = preguntar_por_asesor(formatted_phone_number, message)
        print("Pasamos a preguntar asesor")
    
    elif sentimiento_global == 'mandar_asesor':
        respuesta = mandar_asesor(formatted_phone_number, message)
        print("Pasamos a mandar_asesor")
    
    elif sentimiento_global == 'mandar_prospeccion':
        respuesta = mandar_prospeccion(formatted_phone_number, message)
        print("Pasamos a mandar_prospeccion")

    elif sentimiento_global == 'proveedor':
        respuesta = mandar_proveedor(formatted_phone_number, message)
        print("Pasamos a proveedor")

    elif sentimiento_global == 'desinteres':
        respuesta = mandar_desinteres(formatted_phone_number, message)
        print("Pasamos a mandar_desinteres")

    else:
        if intencion == 'agradecimiento':
            agradecimiento = "Muchas gracias por contactarte con *Diseño y Gestión Inmobilaria* esperamos verte pronto."
            
            send_whatsapp_message(formatted_phone_number, agradecimiento)
            print("Estamos agradecidos")

        elif intencion in ['agendar_cita', 'interes_producto']:
            pregunta_inicial = "¿Te gustaría agendar una cita? 🗓️ "
            send_whatsapp_message(formatted_phone_number, pregunta_inicial)
            sentimiento_global = intencion
            #respuesta = agendar_cita(formatted_phone_number )
            print("Cerrando función contestar_faqs")

        elif intencion in ['compra', 'asesoria', 'informacion_adicional', 'asesor']:
            pregunta_inicial = f"¿Te gustaría hablar con un asesor 👨🏽‍💻 sobre tu próxima inversión en {desarrollo_interesado} 🏢?"
            send_whatsapp_message(formatted_phone_number, pregunta_inicial)
            sentimiento_global = intencion
           # respuesta = preguntar_por_asesor(formatted_phone_number )
            print("Cerrando función contestar_faqs")
        
        elif intencion in ['compra', 'asesoria', 'informacion_adicional', 'asesor']:
            pregunta_inicial = f"¿Te gustaría hablar con un asesor 👨🏽‍💻 sobre tu próxima inversión en {desarrollo_interesado} 🏢?"
            send_whatsapp_message(formatted_phone_number, pregunta_inicial)
            sentimiento_global = intencion
           # respuesta = preguntar_por_asesor(formatted_phone_number )
            print("Cerrando función contestar_faqs")

        elif intencion == 'mandar_asesor':
            sentimiento_global = intencion
            respuesta = mandar_asesor(formatted_phone_number, message)
            print("Cerrando función mandar_asesor")

        elif intencion == 'mandar_prospeccion':
            sentimiento_global = intencion
            respuesta = mandar_prospeccion(formatted_phone_number, message)
            print("Cerrando función mandar_prospeccion")


        elif intencion == 'proveedor':
            pregunta_inicial = f"¿Eres proveedor 🏗️🏙️?"
            send_whatsapp_message(formatted_phone_number, pregunta_inicial)
            sentimiento_global = intencion
           # respuesta = preguntar_por_asesor(formatted_phone_number )
            print("Cerrando función contestar_faqs")

        elif intencion == 'desinteres':
            pregunta_inicial = f"¿Te gustaría hablar de otro de nuestros desarrollos 🏗️🏙️?"
            send_whatsapp_message(formatted_phone_number, pregunta_inicial)
            sentimiento_global = intencion
           # respuesta = preguntar_por_asesor(formatted_phone_number )
            print("Cerrando función contestar_faqs")


        else:
            contestar_faqs(ruta_archivo, message, formatted_phone_number)

def agendar_cita(formatted_phone_number, message):
    global sentimiento_global, desarrollo_final

    print("Iniciando función agendar_cita")
    respuesta_cliente = message
    print("respuesta del cliente=", respuesta_cliente)

    dia_cita, hora_cita = obtener_dia_hora_cita(message)
    print("dia_cita =", dia_cita)
    print("hora_cita =", hora_cita)  # Obtener valores de dia_cita y hora_cita
 

    palabras_clave_positivas = ["sí", "claro", "me interesa", "me gustaría", "si", "ok"]
    palabras_clave_negativas = ["no", "no estoy interesado", "no me interesa"]

    if respuesta_cliente is not None:
        if any(palabra in respuesta_cliente.lower() for palabra in palabras_clave_positivas):
            pedir_hora_fecha = "¿En que día y horario te gustaría programarla? 🗓️ 🕐",
            #send_whatsapp_message(formatted_phone_number, pedir_hora_fecha)
            
        elif any(palabra in respuesta_cliente.lower() for palabra in palabras_clave_negativas):
            #respuesta = contestar_faqs(ruta_archivo, respuesta_cliente, formatted_phone_number)
            ayudarte_mas = "¿Puedo ayudarte en algo más?"
            send_whatsapp_message(formatted_phone_number, ayudarte_mas)
            
            sentimiento_global = None  # Resetear sentimiento_global a None
        else:
            print("No se reconoce ninguna intención.")

    if dia_cita is None and hora_cita is  None:
        dia_hora_agenda = "¿En que día y horario te gustaría programarla? 🗓️ 🕐 \nTenemos un horario de Lunes a Domingo 🗓️  \nde 9:00am a 5:30pm 🕐"
        send_whatsapp_message(formatted_phone_number, dia_hora_agenda)
        ubicacion_de_cita = "Contamos con varios puntos donde podemos recibirte o podemos tener una videollamada \n\n*Madison Loft:* \nhttps://goo.gl/maps/LsjJ5W8ZF75wSD4D6  \n\n*Stelar Bugambilias Residencial:* \nhttps://goo.gl/maps/n9utEDfUZCeEiJpV7 \n\n*Sant Mäarten Lofts:* \nhttps://goo.gl/maps/S1SjV7eqaMXLDFuq8 \n\n*María José Living:* \nhttps://goo.gl/maps/STVTzYERHDWPmeHo8"
        send_whatsapp_message(formatted_phone_number, ubicacion_de_cita)
        print("preguntando por día:")

    if dia_cita is None and hora_cita is not None:
        dia_agenda = "¿Qué día te gustaría agendar?🗓️"
        send_whatsapp_message(formatted_phone_number, dia_agenda)
        print("preguntando por día:")

    if hora_cita is None and dia_cita is not None:
        hora_agenda = "¿A qué hora te gustaría agendar?🕐"
        send_whatsapp_message(formatted_phone_number, hora_agenda)
        print("preguntando por hora")

    if hora_cita is not None and dia_cita is not None:
        respuesta = f"Perfecto {nombre_usuario}, un asesor se pondra en contacto contigo para confirmar tu cita para el día {dia_cita} a la(s) {hora_cita}🕐 🗓️ con el podras ver el lugar de la cita o si será por videollamada "
        send_whatsapp_message(formatted_phone_number, respuesta)

        desarrollo_final = desarrollo_interesado + "_cita"
        print(f"ruta stage:",desarrollo_final)
        pipe_add_person.final_position_deal_cita(person_name, desarrollo_final, dia_cita, hora_cita, archivo_conversacion)


        sentimiento_global = None  # Resetear sentimiento_global a None
        cerrar_conversacion(formatted_phone_number)
        print("Agendado :3 no quiero saber nada xD")
    print("Finalizando función agendar_cita")

def preguntar_por_asesor(formatted_phone_number, message):
    global sentimiento_global, ruta_archivo, contexto, contexto_global, desarrollo_interesado, desarrollo_final # Declarar que se utilizará la variable global

    print("Iniciando función preguntar_por_asesor")
    
    respuesta_cliente = None
    respuesta_cliente= message
    print("respuesta del cliente=", respuesta_cliente)

    palabras_clave_positivas = ["sí", "claro", "me interesa", "me gustaría", "si"]
    palabras_clave_negativas = ["no", "no estoy interesado", "no me interesa"]

    if respuesta_cliente is not None:
        if any(palabra in respuesta_cliente.lower() for palabra in palabras_clave_positivas):

            desarrollo_final = desarrollo_interesado + "_asesor"
            print(f"ruta stage:",desarrollo_final)
            pipe_add_person.final_position_deal_asesor(person_name, desarrollo_final, archivo_conversacion)



            respuesta = "¡Gracias por tu interés! Un asesor se pondrá en contacto contigo pronto👨🏽‍💻"
            send_whatsapp_message(formatted_phone_number, respuesta)
            print("Respuesta positiva enviada:", respuesta)
            sentimiento_global = None
            cerrar_conversacion(formatted_phone_number)

        elif any(palabra in respuesta_cliente.lower() for palabra in palabras_clave_negativas):
            #respuesta = preguntar_por_asesor(ruta_archivo, formatted_phone_number, message)
            respuesta = "¿Te gustaría recibir información de algún otro desarrollo? Invierte en preventa en📍Zona Centro Histórico 📍Zona Minerva📍Zona Chapu 📍Zona Barranca"
            send_whatsapp_message(formatted_phone_number, respuesta)
            print("Respuesta negativa enviada:", respuesta)
            # Resetear sentimiento_global a None
            sentimiento_global = None
            ruta_archivo = None  
            contexto = None
            contexto_global = None
            desarrollo_interesado = None
            
    else:
        print("La respuesta del cliente es None, no se pueden realizar comprobaciones.")

    print("Finalizando función preguntar_por_asesor")

def mandar_desinteres(formatted_phone_number, message):
    global sentimiento_global, ruta_archivo, contexto, contexto_global, desarrollo_interesado  # Declarar que se utilizará la variable global

    print("Iniciando función preguntar_por_asesor")
    
    respuesta_cliente = None
    respuesta_cliente= message
    print("respuesta del cliente=", respuesta_cliente)

    palabras_clave_positivas = ["sí", "claro", "me interesa", "me gustaría", "si"]
    palabras_clave_negativas = ["no", "no estoy interesado", "no me interesa"]

    if respuesta_cliente is not None:
        if any(palabra in respuesta_cliente.lower() for palabra in palabras_clave_positivas):
            verificacion = f"¿De qué desarrollo te gustaría recibir información? 🏢  \n\nSi no conoces el nombre del desarrollo, puedes preguntarme por📍ubicaciones cercanas o 💰rangos de precio."
            send_whatsapp_message(formatted_phone_number, verificacion)
            print("Respuesta positiva enviada:", verificacion)
            sentimiento_global = None
            ruta_archivo = None  
            contexto = None
            contexto_global = None
            desarrollo_interesado = None
        elif any(palabra in respuesta_cliente.lower() for palabra in palabras_clave_negativas):
                        #respuesta = contestar_faqs(ruta_archivo, respuesta_cliente, formatted_phone_number)
            ayudarte_mas = "¿En que más te puedo ayudar?"
            send_whatsapp_message(formatted_phone_number, ayudarte_mas)
            
            sentimiento_global = None  # Resetear sentimiento_global a None
            
    else:
        print("La respuesta del cliente es None, no se pueden realizar comprobaciones.")

    print("Finalizando función preguntar_por_asesor")

def mandar_asesor (formatted_phone_number, message):
    global sentimiento_global  # Declarar que se utilizará la variable global
    print("Iniciando función mandar_asesor")
    
    respuesta_cliente = None
    respuesta_cliente= message
    print("respuesta del cliente=", respuesta_cliente)

    palabras_clave_positivas = ["sí", "claro", "me interesa", "me gustaría", "si"]
    palabras_clave_negativas = ["no", "no estoy interesado", "no me interesa"]

    if respuesta_cliente is not None:
        if any(palabra in respuesta_cliente.lower() for palabra in palabras_clave_positivas):
            desarrollo_final = desarrollo_interesado + "_asesor'"
            print(f"ruta stage:",desarrollo_final)
            pipe_add_person.final_position_deal_asesor(person_name, desarrollo_final)
            respuesta = "¡Gracias por tu interés! 👨🏽‍💻 Un asesor se pondrá en contacto contigo pronto."
            send_whatsapp_message(formatted_phone_number, respuesta)
            print("Respuesta positiva enviada:", respuesta)
        
        elif any(palabra in respuesta_cliente.lower() for palabra in palabras_clave_negativas):
            respuesta = contestar_faqs(ruta_archivo, respuesta_cliente, formatted_phone_number)
            respuesta = "¿En qué más puedo ayudarte?"
            send_whatsapp_message(formatted_phone_number, respuesta)
            print("Respuesta negativa enviada:", respuesta)
            sentimiento_global = None  # Resetear sentimiento_global a None

    else:
        print("La respuesta del cliente es None, no se pueden realizar comprobaciones.")

    print("Finalizando función mandar_asesor")

def mandar_prospeccion (formatted_phone_number, message):
    global sentimiento_global  # Declarar que se utilizará la variable global
    print("Iniciando función mandar_asesor")
    
    sentimiento_global = None
    cerrar_conversacion(formatted_phone_number)
"""     respuesta_cliente = None
    respuesta_cliente= message
    print("respuesta del cliente=", respuesta_cliente)

    palabras_clave_positivas = ["sí", "claro", "me interesa", "me gustaría", "si"]
    palabras_clave_negativas = ["no", "no estoy interesado", "no me interesa"]

    if respuesta_cliente is not None:
        if any(palabra in respuesta_cliente.lower() for palabra in palabras_clave_positivas):
            respuesta = "¡Gracias! prospección se pondrá en contacto contigo pronto."
            send_whatsapp_message(formatted_phone_number, respuesta)
            print("Respuesta positiva enviada:", respuesta)
        elif any(palabra in respuesta_cliente.lower() for palabra in palabras_clave_negativas):
            respuesta = contestar_faqs(ruta_archivo, respuesta_cliente, formatted_phone_number)
            respuesta = "Lamentamos no poder ayudarte 😭😭"
            send_whatsapp_message(formatted_phone_number, respuesta)
            print("Respuesta negativa enviada:", respuesta)
            sentimiento_global = None  # Resetear sentimiento_global a None

    else:
        print("La respuesta del cliente es None, no se pueden realizar comprobaciones.")

    print("Finalizando función mandar_asesor")"""


def mandar_proveedor (formatted_phone_number, message):
    global sentimiento_global  # Declarar que se utilizará la variable global
    print("Iniciando función mandar_asesor")
    
    respuesta_cliente = None
    respuesta_cliente= message
    print("respuesta del cliente=", respuesta_cliente)

    palabras_clave_positivas = ["sí", "claro", "me interesa", "me gustaría", "si"]
    palabras_clave_negativas = ["no", "no estoy interesado", "no me interesa"]

    if respuesta_cliente is not None:
        if any(palabra in respuesta_cliente.lower() for palabra in palabras_clave_positivas):
            respuesta = "Gracias por contactarnos. Nos puedes mandar tu información al correo 👉📨 compras@disenoygestion.mx ."
            send_whatsapp_message(formatted_phone_number, respuesta)
            print("Respuesta positiva enviada:", respuesta)
        elif any(palabra in respuesta_cliente.lower() for palabra in palabras_clave_negativas):
            respuesta = contestar_faqs(ruta_archivo, respuesta_cliente, formatted_phone_number)
            respuesta = "como podemos apoyarte?"
            send_whatsapp_message(formatted_phone_number, respuesta)
            print("Respuesta negativa enviada:", respuesta)
            sentimiento_global = None  # Resetear sentimiento_global a None

    else:
        print("La respuesta del cliente es None, no se pueden realizar comprobaciones.")

    print("Finalizando función proveedor")
    
"""def generar_respuesta_chatgpt(message, respuesta_encontrada):

    # Concatenar la pregunta y la respuesta encontrada como prompt para ChatGPT
    prompt = f"{respuesta_encontrada} \n\n{message} "
    print("ChatGPT está procesando los Datos:", prompt)
    # Generar respuesta con ChatGPT
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        api_key=OPENAI_API_KEY
    )

    # Obtener la respuesta generada por ChatGPT
    respuesta_generada = response.choices[0].text.strip()

    return respuesta_generada"""

def send_whatsapp_multimedia(to, media_urls=None):
    if media_urls:
        for media_url in media_urls:
            message_params = {
                'from_': TWILIO_PHONE_NUMBER,
                'to': f'whatsapp:{to}',  # Número de teléfono del destinatari

                'media_url': media_url
            }
            client.messages.create(**message_params)
            print("Enviado:", media_url)
            print(f"message_params",message_params)

def send_whatsapp_message(to, message):
    client.messages.create(
        from_=TWILIO_PHONE_NUMBER,  # Debe ser un número de teléfono de WhatsApp válido
        body=message,
        to=f'whatsapp:{to}' # Número de teléfono del destinatario
)
    cleaned_message = message.replace('\n\n', ' ')

    nuevo_mensaje_bot = {
        "remitente": "Bot-WhatsApp (Panfilo)",
        "mensaje": message,
        "timestamp": obtener_timestamp_actual()
    }
    historial_conversacion.append(nuevo_mensaje_bot)
    guardar_conversacion_en_archivo(historial_conversacion, archivo_conversacion)

def guardar_conversacion_en_archivo(conversacion, archivo):
    for mensaje in conversacion:
        mensaje['mensaje'] = mensaje['mensaje'].replace('\n\n', ' ')
    
    with open(archivo, 'w', encoding='utf-8') as archivo_salida:
        json.dump(conversacion, archivo_salida, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    app.run(port=65535)