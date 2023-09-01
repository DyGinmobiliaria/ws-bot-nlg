import json

def guardar_conversacion_en_archivo(conversacion, conversacion_de):
    with open(conversacion_de, 'w') as archivo:
        json.dump(conversacion, archivo)

def cargar_conversacion_desde_archivo(conversacion_de):
    try:
        with open(conversacion_de, 'r') as archivo:
            return json.load(archivo)
    except FileNotFoundError:
        return []