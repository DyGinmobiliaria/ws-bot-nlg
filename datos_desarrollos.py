desarrollos = [

    {
        'frase_exacta': 'quisiera recibir información sobre kartesia',
        'nombre': ['kartesia', 'cartezia', 'Kartesia Residencial', 'Cartesia Residencial', 'Kartezia Residencial', 'Cartezia Residencial', 'Kartesia Residential', 'Cartesia Residential',
                    'Kartezia Residential', 'Cartezia Residential', 'Kartesia', 'Cartesia', 'Kartezia'],
        'modelos': ['Lynch', 'Mark', 'Keith', 'Zhen', 'Ellis', 'Bren'],
        'contexto': 'Kartesia Residencial 🏙️ se ubica a solo 600m de Glorieta Minerva y de avenidas principales que conectan a la ciudad. 🌇 Cuenta con depas desde $3 MDP equipados con cocina, clósets, baños, así como amenidades en rooftop panorámico 🤩',
        'ruta_archivo': 'faq_desarrollos/faq_kartesia.json'
    },
    {
        'frase_exacta': 'quisiera recibir información sobre maría josé living',
        'nombre': ['maría josé living', 'majo', 'maria jose', 'María José Living', 'mj', 'Maria José Living', 'Maria Jose Living', 'Mariajose Living', 'Mariajose Living', 'María Living',
                    'Maria Living', 'José Living', 'Jose Living', 'María J Living', 'Maria J Living', 'Mariaj Living', 'María José', 'Maria José', 'Maria Jose', 'Mariajose', 'María J', 'Maria J'],
        'modelos': ['Patria', 'Patria Plus', 'Victoria', 'Victoria Plus', 'Libertad', 'libertad plus', 'libertad balcón', 'Alameda', 'Alameda Plus', 'Alameda Terraza', 'Carmen', 'Carmen Plus',
                    'carmen balcón', 'Alcalde', 'Alcalde Plus', 'Alacalde Balcón', 'Tolsá', 'Tolsa Plus', 'Tolsa balcón'],
        'contexto': 'María José Living cuenta con depas en preventa de 1 y 2 recámaras en zona Centro Histórico 🏙️, con un precio desde 1.6 MDP 💰💼. ¡Maximiza tu inversión! 💵 Divide tu depa en estudios con acceso independiente con la versión FLEX. 🏢🔁💰',
        'ruta_archivo': 'faq_desarrollos/faq_Maria_jose.json'
    },
    {
        'frase_exacta': 'quisiera recibir información sobre sant maärten',
        'nombre': ['Sant Maärten Lofts', 'Sant Maarten Lofts', 'Saint Maärten Lofts', 'Saint Maarten Lofts', 'San Maärten Lofts', 'San Maarten Lofts', 'Sint Maärten Lofts', 'Sint Maarten Lofts',
                    'St. Maärten Lofts', 'St. Maartenx Lofts', 'San Maärten Lofts', 'San Maarten Lofts', 'Sant Maärten', 'Sant Maarten', 'St. Maärten Lofts', 'St. Maarten Lofts', 'Sant Marten', 'san maarten', 'san marten'],
        'modelos': ['Ascend', 'Ascend lock-off', 'Urban', 'Urban Plus', 'Deck', 'Trend'],
        'contexto': 'San Mäarten Lofts 🌆, la nueva manera de generar ingresos extras con nuestro sistema Lock-off. 🔐 Renta una parte o toda la propiedad con accesos independientes.💰🤩 Departamentos desde $2.8 MDP con financiamiento a meses sin intereses ubicados en Gral. San Martín #584, Col. Americana',
        'ruta_archivo': 'faq_desarrollos/faq_Sant_Maarten.json'

    },
    {
        'frase_exacta': 'quisiera recibir información sobre Soneto Residencial',
        'nombre': ['Soneto Residensial','Soneto Residensyal','Soneto Residenssial','Sonetto Residencial','Sonneto Residencial','Soneto Residenciall','Soneto Residenzial',
                    'Soneto Residencialle','Soneto Residenciial','Soneto Ressidencial','Soneto','Sonetto','Soneto Residencia','Soneto Residensial','Soneto Residensyal',
                    'Soneto de Residencia', 'Soneto de Residencial', 'Soneto Residens',],
        'modelos': ['Tipo A', 'Tipo B', 'Tipo C', 'Tipo C Planta Baja', 'Tipo D', 'Tipo D Lock-off','Tipo E','Tipo F','Tipo G','Tipo G Lock-off','Tipo G Terraza',
                    'Tipo G Terraza Lock-off','Tipo H','Tipo H Lock-off','Tipo H Terraza','Tipo H Terraza Lock-off','Tipo I','Tipo I Lock-off'],
        'contexto': '😊 Soneto Residencial cuenta con depas de 1, 2 y 3 recámaras desde 3.6 MDP💰 en la icónica colonia La Americana 🌇. ¡Invierte en la zona más trendy de Guadalajara! 🌟🏢🌆 Una zona de alto interés para el turismo internacional 🌍✈️',
        'ruta_archivo': 'faq_desarrollos/faq_Soneto.json'   
    },
]

def obtener_contexto(message):
    message_lower = message.lower()

    # Buscar coincidencia en los desarrollos
    for desarrollo in desarrollos:
        # Verificar si el mensaje contiene la frase exacta
        if message_lower in desarrollo['frase_exacta'].lower():
            ruta_archivo = desarrollo['ruta_archivo']
            contexto = desarrollo['contexto']
            print(f"Contexto encontrado desarrollo: {contexto}")
            return contexto, ruta_archivo

        # Buscar coincidencia en los nombres de los desarrollos
        for nombre in desarrollo['nombre']:
            if nombre.lower() in message_lower:
                ruta_archivo = desarrollo['ruta_archivo']
                contexto = desarrollo['contexto']
                print(f"Contexto encontrado nombre: {contexto}")
                return contexto, ruta_archivo

        # Buscar coincidencia en los modelos de los desarrollos
        for modelo in desarrollo['modelos']:
            if modelo.lower() in message_lower:
                ruta_archivo = desarrollo['ruta_archivo']
                contexto = desarrollo['contexto']
                print(f"Contexto encontrado modelo: {contexto}")
                return contexto, ruta_archivo

    # Si no se encontró ninguna coincidencia, retornar None
    return None, None


