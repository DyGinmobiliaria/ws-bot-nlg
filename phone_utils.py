import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException, PhoneNumberFormat

def process_phone_number(phone_number_string, country_code='MX'):
    try:
        phone_number = phonenumbers.parse(phone_number_string, country_code)

        if phonenumbers.is_valid_number(phone_number):
            formatted_phone_number = phonenumbers.format_number(phone_number, PhoneNumberFormat.E164)
            print(f"Número formateado: {formatted_phone_number}")  # Agrega esta línea para imprimir el número

            return formatted_phone_number
        else:
            raise ValueError('Número de teléfono inválido')
    except NumberParseException as e:
        raise ValueError(f'Número de teléfono inválido: {e}')
