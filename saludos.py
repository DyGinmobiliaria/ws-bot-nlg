import datetime

def obtener_saludo():
    # Obtener la hora actual
    hora_actual = datetime.datetime.now().time()

    # Definir los límites de tiempo para los saludos
    limite_manana = datetime.time(12, 0)  # Hasta las 12:00 PM
    limite_tarde = datetime.time(20, 0)   # Hasta las 6:00 PM

    # Obtener el saludo según la hora actual
    if hora_actual < limite_manana:
        saludo = "¡Hola, buenos días"
    elif hora_actual < limite_tarde:
        saludo = "¡Hola, buenas tardes"
    else:
        saludo = "¡Hola, buenas noches"
    
    return saludo