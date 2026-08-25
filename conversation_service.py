# ==========================================
# CONVERSACIONES PENDIENTES
# ==========================================

# Diccionario que almacena temporalmente las conversaciones
# que todavía necesitan información del usuario.
#
# La estructura funciona aproximadamente así:
#
# {
#     user_id: datos_de_la_solicitud
# }
#
# Por ejemplo, si el usuario dice:
#
# "Agenda una reunión"
#
# pero no dice qué día, la IA puede determinar que falta
# la fecha.
#
# Entonces podemos guardar la información pendiente
# asociándola al ID del usuario.
#
# En palabras sencillas:
# es como una pequeña libreta en memoria donde el bot
# apunta:
#
# "A este usuario todavía le debo completar una solicitud".
conversaciones = {}


# ==========================================
# CONFIRMACIONES PENDIENTES
# ==========================================

# Diccionario que almacena temporalmente las acciones
# que están esperando una confirmación del usuario.
#
# Esto será útil cuando el bot detecte, por ejemplo,
# que existe un conflicto de horario.
#
# Ejemplo:
#
# Usuario:
# "Agenda una reunión mañana a las 12"
#
# El bot revisa el calendario y descubre que ya existe
# un evento de 12:00 PM a 1:00 PM.
#
# Entonces puede guardar aquí el evento que estaba
# intentando crear mientras espera que el usuario responda:
#
# "¿Deseas agendarlo de todas formas?"
#
# En palabras sencillas:
# es otra libreta, pero esta vez sirve para recordar
# "estoy esperando que esta persona me diga sí o no".
confirmaciones = {}


# ==========================================
# CONVERSACIONES
# ==========================================

# ----------------------------------------------------------
# OBTENER CONVERSACIÓN
# ----------------------------------------------------------

def obtener_conversacion(user_id):

    # Busca si existe una conversación pendiente
    # asociada al ID del usuario.
    #
    # .get() permite obtener el valor del diccionario.
    #
    # Si el usuario existe en el diccionario:
    # devuelve los datos guardados.
    #
    # Si no existe:
    # devuelve None.
    #
    # En palabras sencillas:
    # "¿Tengo algo pendiente con este usuario?"
    return conversaciones.get(user_id)


# ----------------------------------------------------------
# GUARDAR CONVERSACIÓN
# ----------------------------------------------------------

def guardar_conversacion(user_id, datos):

    # Guarda los datos de una conversación pendiente
    # utilizando el ID del usuario como identificador.
    #
    # Si el usuario ya tenía información guardada,
    # esta línea la reemplaza por los nuevos datos.
    #
    # Ejemplo conceptual:
    #
    # conversaciones[12345] = datos
    #
    # En palabras sencillas:
    # "Guarda esta conversación y recuerda que pertenece
    # al usuario 12345".
    conversaciones[user_id] = datos


# ----------------------------------------------------------
# ELIMINAR CONVERSACIÓN
# ----------------------------------------------------------

def eliminar_conversacion(user_id):

    # Antes de eliminar la conversación, comprobamos
    # si realmente existe una conversación guardada
    # para ese usuario.
    if user_id in conversaciones:

        # 'del' elimina la información asociada a ese usuario.
        #
        # Esto normalmente ocurre cuando la solicitud ya
        # fue completada y ya no necesitamos conservar
        # información pendiente.
        #
        # En palabras sencillas:
        # "Ya terminamos esta conversación pendiente,
        # puedes borrar la nota de la libreta".
        del conversaciones[user_id]


# ==========================================
# CONFIRMACIONES
# ==========================================

# ----------------------------------------------------------
# OBTENER CONFIRMACIÓN
# ----------------------------------------------------------

def obtener_confirmacion(user_id):

    # Busca si existe una confirmación pendiente para
    # el usuario indicado.
    #
    # Si existe:
    # devuelve los datos que estaban esperando confirmación.
    #
    # Si no existe:
    # devuelve None.
    #
    # En palabras sencillas:
    # "¿Tengo alguna pregunta pendiente esperando
    # una respuesta de este usuario?"
    return confirmaciones.get(user_id)


# ----------------------------------------------------------
# GUARDAR CONFIRMACIÓN
# ----------------------------------------------------------

def guardar_confirmacion(user_id, datos):

    # Guarda los datos de una acción que necesita
    # confirmación.
    #
    # El ID del usuario permite saber a quién pertenece
    # esa confirmación.
    #
    # Ejemplo:
    #
    # confirmaciones[12345] = datos
    #
    # Así, cuando el usuario responda "sí" o "no",
    # el bot podrá recuperar exactamente qué acción
    # estaba esperando confirmación.
    #
    # En palabras sencillas:
    # "Guarda esta situación porque necesito preguntarle
    # algo al usuario antes de continuar".
    confirmaciones[user_id] = datos


# ----------------------------------------------------------
# ELIMINAR CONFIRMACIÓN
# ----------------------------------------------------------

def eliminar_confirmacion(user_id):

    # Comprobamos si existe una confirmación pendiente
    # para ese usuario.
    if user_id in confirmaciones:

        # Eliminamos la confirmación almacenada.
        #
        # Esto se hace cuando el usuario ya respondió
        # y la situación dejó de estar pendiente.
        #
        # En palabras sencillas:
        # "Ya me respondió. Ya no necesito guardar
        # esta nota".
        del confirmaciones[user_id]