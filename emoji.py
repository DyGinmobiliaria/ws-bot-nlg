
def assign_emojis(answer):
    message_with_emoji = answer

    if any(keyword in answer for keyword in ['departamentos', 'Departamento', 'Depa', 'desarrollos', 'desarrollo']):
        message_with_emoji += ' 🏢 '
    elif any(keyword in answer for keyword in ['precio', 'costo', 'Costos', 'Precios']):
        message_with_emoji += ' 💰 '
    elif any(keyword in answer for keyword in ['características', 'Amenidades', 'Caracteristica', 'Amenidad', 'amenities']):
        message_with_emoji += ' ⭐️ '
    elif any(keyword in answer for keyword in ['ubicación', 'ubicado', 'ub¡cados']):
        message_with_emoji += '📍'
    elif any(keyword in answer for keyword in ['pago', 'pagos']):
        message_with_emoji += ' 💳 '

    return message_with_emoji
