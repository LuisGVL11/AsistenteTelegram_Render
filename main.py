# ============================================================
# IMPORTAR LIBRERÍAS
# ============================================================

# 'os' permite interactuar con variables de entorno del
# sistema operativo.
#
# En este proyecto lo utilizamos para obtener el token
# secreto de Telegram desde el archivo .env.
import os


# 'requests' permite realizar peticiones HTTP.
#
# En este archivo actualmente se importa, aunque las
# peticiones a Apps Script se realizan principalmente desde
# calendar_service.py.
#
# No se elimina porque estamos documentando el código existente
# sin modificarlo.
import requests


# 'datetime' permite trabajar con fechas y horas.
#
# Lo utilizamos para:
# - convertir horas
# - comparar horarios
# - convertir fechas
# - determinar el día de la semana
# - detectar conflictos entre eventos
import datetime


# ============================================================
# IMPORTAR FUNCIONES DE INTELIGENCIA ARTIFICIAL
# ============================================================

# Importamos las funciones encargadas de comunicarse con
# Gemini y convertir los mensajes del usuario en una acción
# que el programa pueda entender.
#
# interpretar_mensaje:
# recibe un mensaje nuevo y Gemini determina qué quiere
# hacer el usuario.
#
# completar_informacion:
# se utiliza cuando existe una conversación pendiente y
# el usuario está proporcionando la información que faltaba.
from ai_service import (
    interpretar_mensaje,
    completar_informacion
)


# ============================================================
# IMPORTAR FUNCIONES DEL CALENDARIO
# ============================================================

# Estas funciones permiten comunicarnos con Google Calendar
# a través de Google Apps Script.
#
# crear_evento:
# crea un evento.
#
# consultar_eventos:
# obtiene eventos existentes.
#
# consultar_horas_libres:
# calcula y devuelve los horarios disponibles.
from calendar_service import (
    crear_evento,
    consultar_eventos,
    consultar_horas_libres
)


# ============================================================
# IMPORTAR FUNCIONES DE CONVERSACIONES
# ============================================================

# Estas funciones permiten guardar temporalmente información
# relacionada con cada usuario.
#
# Las primeras tres manejan solicitudes incompletas.
#
# Las últimas tres manejan situaciones que necesitan una
# confirmación de "sí" o "no".
from conversation_service import (
    obtener_conversacion,
    guardar_conversacion,
    eliminar_conversacion,
    obtener_confirmacion,
    guardar_confirmacion,
    eliminar_confirmacion
)


# Carga las variables almacenadas en el archivo .env.
from dotenv import load_dotenv


# Update representa un mensaje o evento recibido desde Telegram.
#
# Por ejemplo, cuando el usuario escribe:
#
# "Agenda una reunión mañana"
#
# Telegram envía esa información al bot dentro de un Update.
from telegram import Update


# Importamos herramientas de python-telegram-bot.
#
# ApplicationBuilder:
# construye la aplicación del bot.
#
# CommandHandler:
# permite responder a comandos como /start.
#
# MessageHandler:
# permite procesar mensajes normales.
#
# ContextTypes:
# contiene información adicional de cada actualización.
#
# filters:
# permite decidir qué tipos de mensajes queremos procesar.
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# ============================================================
# CARGAR VARIABLES DE ENTORNO
# ============================================================

# Lee el archivo .env y carga sus variables.
#
# En palabras sencillas:
# "trae las configuraciones secretas que están fuera
# del código".
load_dotenv()


# Obtiene el token del bot de Telegram desde las variables
# de entorno.
#
# Ese token es lo que permite que nuestro programa se
# conecte con el bot creado en Telegram.
TOKEN = os.getenv("BOT_TOKEN")


# ============================================================
# FUNCIÓN PARA FORMATEAR HORA
# ============================================================

def formatear_hora(hora):

    # Si no recibimos ninguna hora, devolvemos una cadena vacía.
    #
    # Esto evita intentar convertir un valor inexistente.
    if not hora:
        return ""


    try:

        # Convierte una hora en formato de 24 horas:
        #
        # "14:30"
        #
        # en un objeto de fecha/hora de Python.
        #
        # "%H:%M" significa:
        # %H = hora en formato 24 horas
        # %M = minutos
        hora_objeto = datetime.datetime.strptime(
            hora,
            "%H:%M"
        )


        # Convierte la hora al formato de 12 horas:
        #
        # "14:30" → "02:30 PM"
        #
        # "%I" = hora en formato 12 horas
        # "%M" = minutos
        # "%p" = AM o PM
        #
        # lstrip("0") elimina el cero inicial.
        #
        # "02:30 PM" → "2:30 PM"
        return hora_objeto.strftime(
            "%I:%M %p"
        ).lstrip("0")


    except Exception:

        # Si por alguna razón la hora no puede convertirse,
        # simplemente devolvemos el valor original.
        #
        # Así evitamos que el bot se caiga solamente porque
        # una hora llegó en un formato inesperado.
        return hora

# ============================================================
# DETECTAR CONFLICTO DE HORARIOS
# ============================================================

def detectar_conflicto(
    accion,
    eventos
):

    # Intentamos realizar todas las conversiones y
    # comparaciones de horarios dentro de un bloque protegido.
    try:

        # Convierte la hora de inicio del nuevo evento
        # desde texto:
        #
        # "12:00"
        #
        # a un objeto de hora que Python pueda comparar.
        nueva_hora_inicio = datetime.datetime.strptime(
            accion.hora_inicio,
            "%H:%M"
        ).time()


        # Hace lo mismo con la hora de finalización.
        nueva_hora_fin = datetime.datetime.strptime(
            accion.hora_fin,
            "%H:%M"
        ).time()


        # Convierte la fecha del nuevo evento:
        #
        # "2026-08-20"
        #
        # a un objeto date de Python.
        nueva_fecha = datetime.datetime.strptime(
            accion.fecha,
            "%Y-%m-%d"
        ).date()


        # Combina la fecha y la hora de inicio para obtener
        # una fecha y hora completa.
        #
        # Ejemplo:
        #
        # 2026-08-20 + 12:00
        #
        # se convierte en:
        #
        # 2026-08-20 12:00
        nuevo_inicio = datetime.datetime.combine(
            nueva_fecha,
            nueva_hora_inicio
        )


        # Hace lo mismo para la hora de finalización.
        nuevo_fin = datetime.datetime.combine(
            nueva_fecha,
            nueva_hora_fin
        )


        # Recorremos todos los eventos que ya existen
        # en ese día.
        #
        # "eventos" viene de Google Calendar.
        for evento in eventos:

            # Obtiene la fecha y hora de inicio del evento
            # existente.
            inicio = evento.get(
                "inicio",
                ""
            )


            # Obtiene la fecha y hora de finalización.
            fin = evento.get(
                "fin",
                ""
            )


            # Si el evento no tiene inicio o final,
            # no podemos compararlo.
            #
            # Por eso simplemente pasamos al siguiente.
            if not inicio or not fin:

                continue


            # Convierte el inicio del evento existente
            # a un objeto datetime.
            inicio_evento = datetime.datetime.strptime(
                inicio,
                "%Y-%m-%d %H:%M"
            )


            # Convierte la finalización del evento existente
            # a un objeto datetime.
            fin_evento = datetime.datetime.strptime(
                fin,
                "%Y-%m-%d %H:%M"
            )


            # ==========================================
            # COMPROBAR SOLAPAMIENTO
            # ==========================================

            # Aquí está la parte más importante de esta función.
            #
            # Comprobamos si el nuevo evento ocupa algún momento
            # que ya está ocupado por otro evento.
            #
            # La condición significa:
            #
            # El nuevo evento empieza antes de que termine
            # el evento existente
            #
            # Y además:
            #
            # El nuevo evento termina después de que empiece
            # el evento existente.
            #
            # Si ambas cosas son ciertas, los horarios se
            # superponen.
            #
            # Ejemplo:
            #
            # Evento existente:
            # 12:00 - 13:00
            #
            # Nuevo:
            # 12:00 - 14:00
            #
            # Existe conflicto.
            if (
                nuevo_inicio < fin_evento
                and
                nuevo_fin > inicio_evento
            ):

                # Devolvemos el evento que está provocando
                # el conflicto.
                return evento


        # Si recorremos todos los eventos y ninguno se
        # superpone, devolvemos None.
        #
        # None significa:
        # "No encontré ningún conflicto".
        return None


    except Exception as e:

        # Si ocurre algún problema convirtiendo fechas,
        # horas o comparando valores, mostramos el error
        # en la consola.
        print(
            "Error detectando conflicto:",
            e
        )

        # En caso de error devolvemos None.
        return None


# ============================================================
# INICIO
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # Envía un mensaje al usuario cuando utiliza el comando
    # /start.
    #
    # update.message representa el mensaje que llegó desde
    # Telegram.
    #
    # reply_text() envía una respuesta al usuario.
    await update.message.reply_text(
        "👋 ¡Hola! Soy tu asistente personal de agenda."
    )


# ============================================================
# RESPONDER MENSAJES
# ============================================================

async def responder(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # Obtiene el texto que escribió el usuario.
    #
    # Ejemplo:
    #
    # "Agenda una reunión mañana a las 12"
    mensaje = update.message.text


    # Obtiene el identificador único del usuario de Telegram.
    #
    # Este ID permite saber quién está hablando con el bot.
    #
    # También se utiliza para guardar conversaciones
    # y confirmaciones asociadas a esa persona.
    user_id = update.message.from_user.id

        # ==========================================
    # COMPROBAR CONFIRMACIÓN PENDIENTE
    # ==========================================

    # Revisamos si este usuario tiene alguna acción esperando
    # una respuesta de "sí" o "no".
    #
    # Esto es importante para los conflictos de horario.
    confirmacion = obtener_confirmacion(
        user_id
    )


    # Si existe una confirmación pendiente, significa que
    # el mensaje actual probablemente es la respuesta
    # a esa pregunta.
    if confirmacion:

        # Convertimos la respuesta a minúsculas y eliminamos
        # espacios innecesarios.
        #
        # Ejemplo:
        #
        # "  Sí  " → "sí"
        respuesta = mensaje.strip().lower()


        # ==========================================
        # USUARIO ACEPTA
        # ==========================================

        # Comprobamos diferentes formas de decir "sí".
        #
        # Permitimos:
        # si
        # sí
        # s
        # yes
        if respuesta in [
            "si",
            "sí",
            "s",
            "yes"
        ]:

            # Recuperamos la acción que estaba esperando
            # confirmación.
            #
            # Esta es la acción original que el usuario
            # quería ejecutar.
            accion = confirmacion["accion"]


            print(
                "CONFIRMACIÓN RECIBIDA: SÍ"
            )


            try:

                # Ahora sí creamos el evento.
                #
                # Esto ocurre porque el usuario confirmó
                # que desea crearlo aunque exista conflicto.
                resultado = crear_evento(
                    accion
                )

            except Exception as e:

                # Si ocurre un error comunicándonos con
                # el calendario, lo mostramos en consola.
                print(
                    "Error calendario:",
                    e
                )


                # Eliminamos la confirmación porque la
                # operación ya no continuará.
                eliminar_confirmacion(
                    user_id
                )


                await update.message.reply_text(
                    "❌ No pude crear el evento."
                )

                return


            # Eliminamos la confirmación porque el usuario
            # ya respondió.
            #
            # Ya no necesitamos recordar esa situación.
            eliminar_confirmacion(
                user_id
            )


            # Comprobamos si Google Apps Script informó
            # que el evento se creó correctamente.
            if resultado.get("estado") == "ok":

                # Convertimos las horas al formato de 12 horas
                # para mostrarlas de manera más amigable.
                hora_inicio_formateada = formatear_hora(
                    accion.hora_inicio
                )

                hora_fin_formateada = formatear_hora(
                    accion.hora_fin
                )


                # Construimos el mensaje que verá el usuario.
                mensaje_respuesta = (
                    "✅ Evento creado.\n\n"
                    f"📌 {accion.titulo}\n"
                    f"📅 {accion.fecha}\n"
                    f"⏰ {hora_inicio_formateada} - "
                    f"{hora_fin_formateada}"
                )


                # Si el evento tiene repetición, la mostramos.
                if accion.repeticion:

                    if accion.repeticion == "semanal":

                        mensaje_respuesta += (
                            "\n🔁 Repetición: semanal"
                        )

                    elif accion.repeticion == "mensual":

                        mensaje_respuesta += (
                            "\n🔁 Repetición: mensual"
                        )


                # Si el evento tiene recordatorios,
                # también los mostramos.
                if accion.recordatorios_dias:

                    # Convertimos cada número a texto y
                    # los unimos mediante ", ".
                    #
                    # Ejemplo:
                    #
                    # [14, 7]
                    #
                    # se convierte en:
                    #
                    # "14, 7"
                    recordatorios = ", ".join(
                        str(x)
                        for x in accion.recordatorios_dias
                    )

                    mensaje_respuesta += (
                        f"\n🔔 Recordatorios: "
                        f"{recordatorios} día(s) antes"
                    )


                # Enviamos la confirmación final al usuario.
                await update.message.reply_text(
                    mensaje_respuesta
                )

            else:

                # Si Apps Script no devolvió estado "ok",
                # mostramos el resultado para poder
                # diagnosticar el problema.
                print(
                    "Error Apps Script:",
                    resultado
                )

                await update.message.reply_text(
                    "❌ Hubo un error creando el evento."
                )

            return


        # ==========================================
        # USUARIO RECHAZA
        # ==========================================

        # Comprobamos diferentes maneras de decir "no".
        if respuesta in [
            "no",
            "n",
            "nop"
        ]:

            print(
                "CONFIRMACIÓN RECIBIDA: NO"
            )


            # Eliminamos la confirmación pendiente porque
            # el usuario ya tomó una decisión.
            eliminar_confirmacion(
                user_id
            )


            # Informamos al usuario que no se creó el evento.
            await update.message.reply_text(
                "👍 Entendido. No se creó el evento."
            )

            return


        # ==========================================
        # RESPUESTA NO RECONOCIDA
        # ==========================================

        # Si el usuario tenía una confirmación pendiente
        # pero respondió algo diferente de sí/no,
        # le pedimos que responda nuevamente.
        await update.message.reply_text(
            "Por favor responde **sí** o **no**."
        )

        return


    # Si no había ninguna confirmación pendiente,
    # el mensaje se procesa normalmente.
    await update.message.reply_text(
        "🤖 Analizando..."
    )


    # ==========================================
    # INTERPRETAR MENSAJE
    # ==========================================

    try:

        # Comprobamos si el usuario tiene una conversación
        # pendiente.
        conversacion = obtener_conversacion(user_id)


        # Si existe una conversación pendiente, significa que
        # anteriormente faltaba información.
        if conversacion:

            print(
                "COMPLETANDO INFORMACION PENDIENTE"
            )

            # Enviamos a Gemini la conversación anterior
            # junto con la nueva respuesta del usuario.
            #
            # Ejemplo:
            #
            # Bot:
            # "¿Qué día?"
            #
            # Usuario:
            # "Mañana"
            #
            # completar_informacion() completa la solicitud.
            accion = completar_informacion(
                conversacion,
                mensaje
            )

        else:

            # Si no existe una conversación pendiente,
            # interpretamos el mensaje como una solicitud
            # completamente nueva.
            accion = interpretar_mensaje(
                mensaje
            )


    except Exception as e:

        # Si ocurre un error durante la comunicación con
        # Gemini o durante el procesamiento de la respuesta,
        # mostramos el error en consola.
        print("Error IA:", e)

        await update.message.reply_text(
            "⚠️ La IA no respondió correctamente. "
            "Intenta nuevamente."
        )

        return


    # Mostramos en consola la acción que Gemini interpretó.
    #
    # Esto es muy útil durante el desarrollo porque podemos
    # comprobar qué entendió realmente la IA.
    print("ACCION RECIBIDA:")
    print(accion)


    # ==========================================
    # CREAR EVENTO
    # ==========================================

    # Comprobamos si la IA determinó que el usuario
    # quiere crear un evento.
    if accion.accion == "crear_evento":

        # Si faltan datos obligatorios, todavía no creamos
        # el evento.
        if accion.faltantes:

            print(
                "GUARDANDO CONVERSACION"
            )

            # Guardamos la solicitud incompleta para poder
            # continuarla cuando el usuario proporcione
            # la información que falta.
            guardar_conversacion(
                user_id,
                accion
            )

            # Convertimos la lista de datos faltantes
            # en un texto separado por comas.
            faltantes = ", ".join(
                accion.faltantes
            )

            await update.message.reply_text(
                f"Me falta esta información: {faltantes}"
            )

            return

                # ==========================================
        # COMPROBAR CONFLICTOS
        # ==========================================

        # Antes de crear un evento, consultamos Google Calendar
        # para revisar si ya existe otro evento ese mismo día.
        try:

            resultado_consulta = consultar_eventos(
                accion.fecha,
                accion.fecha,
                ""
            )

        except Exception as e:

            print(
                "Error comprobando conflictos:",
                e
            )

            await update.message.reply_text(
                "❌ No pude comprobar si existe "
                "un conflicto de horario."
            )

            return


        # Verificamos que la consulta a Google Calendar
        # haya sido exitosa.
        if resultado_consulta.get("estado") != "ok":

            await update.message.reply_text(
                "❌ No pude comprobar el calendario."
            )

            return


        # Obtenemos la lista de eventos existentes.
        #
        # Si no existe la clave "eventos", utilizamos
        # una lista vacía.
        eventos_existentes = resultado_consulta.get(
            "eventos",
            []
        )


        # Comparamos el nuevo evento contra los eventos
        # existentes para determinar si existe solapamiento.
        conflicto = detectar_conflicto(
            accion,
            eventos_existentes
        )


        # ==========================================
        # EXISTE CONFLICTO
        # ==========================================

        # Si detectar_conflicto() devuelve un evento,
        # significa que encontramos un choque de horarios.
        if conflicto:

            print(
                "CONFLICTO DETECTADO:"
            )

            print(
                conflicto
            )


            # Guardamos la acción que el usuario quería realizar
            # para poder recuperarla después de que responda
            # "sí" o "no".
            guardar_confirmacion(
                user_id,
                {
                    "tipo": "crear_evento_conflicto",
                    "accion": accion
                }
            )


            # Obtenemos el título del evento que ya existe.
            titulo_conflicto = conflicto.get(
                "titulo",
                "Evento existente"
            )


            # Obtenemos la hora de inicio del evento existente.
            inicio_conflicto = conflicto.get(
                "inicio",
                ""
            )


            # Obtenemos la hora de finalización del evento existente.
            fin_conflicto = conflicto.get(
                "fin",
                ""
            )


            # Inicializamos las variables que almacenarán
            # las horas del evento que está causando conflicto.
            hora_inicio_conflicto = ""

            hora_fin_conflicto = ""


            # Si la fecha y hora de inicio vienen juntas,
            # separamos la fecha de la hora.
            #
            # Ejemplo:
            #
            # "2026-08-20 12:00"
            #
            # se convierte en:
            #
            # fecha = "2026-08-20"
            # hora = "12:00"
            if " " in inicio_conflicto:

                _, hora_inicio_conflicto = (
                    inicio_conflicto.split(
                        " ",
                        1
                    )
                )


            # Hacemos lo mismo con la hora de finalización.
            if " " in fin_conflicto:

                _, hora_fin_conflicto = (
                    fin_conflicto.split(
                        " ",
                        1
                    )
                )


            # Convertimos las horas del evento existente
            # al formato AM/PM.
            hora_inicio_conflicto = formatear_hora(
                hora_inicio_conflicto
            )

            hora_fin_conflicto = formatear_hora(
                hora_fin_conflicto
            )


            # Convertimos también las horas del nuevo evento.
            hora_inicio_nuevo = formatear_hora(
                accion.hora_inicio
            )

            hora_fin_nuevo = formatear_hora(
                accion.hora_fin
            )


            # Le mostramos al usuario el evento que ya existe
            # y el nuevo evento que quiere crear.
            #
            # Luego le pedimos una decisión.
            await update.message.reply_text(

                "⚠️ Ya tienes un evento en ese horario.\n\n"

                f"📌 {titulo_conflicto}\n"
                f"⏰ {hora_inicio_conflicto} - "
                f"{hora_fin_conflicto}\n\n"

                f"Quieres agendar igualmente:\n"
                f"📌 {accion.titulo}\n"
                f"⏰ {hora_inicio_nuevo} - "
                f"{hora_fin_nuevo}\n\n"

                "Responde **sí** o **no**."

            )

            return


        # Si no existe conflicto, podemos intentar crear
        # directamente el evento.
        try:

            resultado = crear_evento(
                accion
            )

        except Exception as e:

            print(
                "Error calendario:",
                e
            )

            await update.message.reply_text(
                "❌ No pude crear el evento."
            )

            return


        # Comprobamos si Apps Script indicó que la creación
        # fue exitosa.
        if resultado.get("estado") == "ok":

            # Eliminamos cualquier conversación pendiente
            # relacionada con este usuario.
            eliminar_conversacion(
                user_id
            )


            # Convertimos las horas al formato AM/PM.
            hora_inicio_formateada = formatear_hora(
                accion.hora_inicio
            )

            hora_fin_formateada = formatear_hora(
                accion.hora_fin
            )


            # Construimos el mensaje de confirmación.
            mensaje_respuesta = (
                "✅ Evento creado.\n\n"
                f"📌 {accion.titulo}\n"
                f"📅 {accion.fecha}\n"
                f"⏰ {hora_inicio_formateada} - "
                f"{hora_fin_formateada}"
            )


            # ==========================================
            # REPETICIÓN
            # ==========================================

            # Si el evento se repite, mostramos el tipo
            # de repetición.
            if accion.repeticion:

                if accion.repeticion == "semanal":

                    mensaje_respuesta += (
                        "\n🔁 Repetición: semanal"
                    )

                elif accion.repeticion == "mensual":

                    mensaje_respuesta += (
                        "\n🔁 Repetición: mensual"
                    )


            # ==========================================
            # RECORDATORIOS
            # ==========================================

            # Si existen recordatorios configurados,
            # los mostramos en la respuesta.
            if accion.recordatorios_dias:

                # Convertimos los números de días a texto.
                recordatorios = ", ".join(
                    str(x)
                    for x in accion.recordatorios_dias
                )

                mensaje_respuesta += (
                    f"\n🔔 Recordatorios: "
                    f"{recordatorios} día(s) antes"
                )


            # Enviamos la respuesta final al usuario.
            await update.message.reply_text(
                mensaje_respuesta
            )


        else:

            # Si Apps Script devolvió un error,
            # mostramos la respuesta para poder diagnosticarlo.
            print(
                "Error Apps Script:",
                resultado
            )

            await update.message.reply_text(
                "❌ Hubo un error creando el evento."
            )

        return


    # ==========================================
    # CONSULTAR EVENTOS
    # ==========================================

    # Comprobamos si el usuario quiere consultar
    # eventos existentes.
    if accion.accion == "consultar_eventos":

        try:

            # Consultamos Google Calendar utilizando:
            #
            # fecha_inicio
            # fecha_fin
            # filtro_titulo
            #
            # Esto permite consultar desde un día concreto
            # hasta otro y, opcionalmente, filtrar por título.
            resultado = consultar_eventos(
                accion.fecha_inicio,
                accion.fecha_fin,
                accion.filtro_titulo
            )

        except Exception as e:

            print(
                "Error consultando calendario:",
                e
            )

            await update.message.reply_text(
                "❌ No pude consultar el calendario."
            )

            return


        # Comprobamos que la consulta haya sido exitosa.
        if resultado.get("estado") != "ok":

            await update.message.reply_text(
                "❌ Hubo un error consultando "
                "el calendario."
            )

            return


        # Extraemos la lista de eventos de la respuesta.
        eventos = resultado.get(
            "eventos",
            []
        )


        # Si no hay eventos, informamos al usuario.
        if not eventos:

            await update.message.reply_text(
                "📅 No tienes eventos agendados "
                "en ese periodo."
            )

            return


        # ==========================================
        # CONSTRUIR RESPUESTA
        # ==========================================

        # Comenzamos el mensaje que se enviará a Telegram.
        texto = "📅 Esto es lo que tienes agendado:"


        # Lista de nombres de los días de la semana.
        #
        # Python representa los días de la semana mediante
        # números:
        #
        # 0 = lunes
        # 1 = martes
        # ...
        # 6 = domingo
        #
        # Esta lista permite convertir esos números a nombres
        # en español.
        dias_semana = [
            "Lunes",
            "Martes",
            "Miércoles",
            "Jueves",
            "Viernes",
            "Sábado",
            "Domingo"
        ]


        # Lista de nombres de los meses en español.
        meses = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre"
        ]


        # Recorremos todos los eventos encontrados.
        for evento in eventos:

            # Obtenemos el título del evento.
            #
            # Si no existe, utilizamos "Sin título".
            titulo = evento.get(
                "titulo",
                "Sin título"
            )

            # Obtenemos fecha y hora de inicio.
            inicio = evento.get(
                "inicio",
                ""
            )

            # Obtenemos fecha y hora de finalización.
            fin = evento.get(
                "fin",
                ""
            )


            # ==========================================
            # EXTRAER FECHA Y HORA
            # ==========================================

            # Variables que almacenarán por separado
            # la fecha y las horas.
            fecha_evento = ""

            hora_inicio = ""

            hora_fin = ""


            # Si existe un espacio en el valor de inicio,
            # significa que probablemente tenemos:
            #
            # "2026-08-18 10:00"
            #
            # Separamos fecha y hora.
            if " " in inicio:

                fecha_evento, hora_inicio = (
                    inicio.split(" ", 1)
                )

            else:

                # Si no existe espacio, tratamos todo el
                # valor como fecha.
                fecha_evento = inicio


            # Hacemos lo mismo con la hora de finalización.
            if " " in fin:

                _, hora_fin = (
                    fin.split(" ", 1)
                )

            else:

                hora_fin = fin


            # ==========================================
            # FORMATEAR HORA A 12 HORAS
            # ==========================================

            # Convertimos las horas de formato 24 horas
            # a formato AM/PM.
            hora_inicio_formateada = formatear_hora(
                hora_inicio
            )

            hora_fin_formateada = formatear_hora(
                hora_fin
            )


            # ==========================================
            # CONVERTIR FECHA
            # ==========================================

            try:

                # Separamos la fecha:
                #
                # "2026-08-18"
                #
                # en:
                #
                # ["2026", "08", "18"]
                partes_fecha = fecha_evento.split("-")

                año = int(partes_fecha[0])
                mes = int(partes_fecha[1])
                dia = int(partes_fecha[2])


                # Creamos un objeto date de Python.
                fecha_objeto = datetime.date(
                    año,
                    mes,
                    dia
                )


                # weekday() devuelve un número entre 0 y 6.
                #
                # Utilizamos ese número para obtener el nombre
                # del día de nuestra lista.
                dia_semana = dias_semana[
                    fecha_objeto.weekday()
                ]


                # El mes empieza en 1, pero las listas empiezan
                # en 0, por eso usamos mes - 1.
                nombre_mes = meses[
                    mes - 1
                ]


                # Construimos una fecha más amigable.
                #
                # Ejemplo:
                #
                # "Martes 18 de agosto"
                fecha_formateada = (
                    f"{dia_semana} "
                    f"{dia} de "
                    f"{nombre_mes}"
                )


            except Exception:

                # Si no podemos convertir la fecha,
                # utilizamos el valor original.
                fecha_formateada = fecha_evento


            # ==========================================
            # AGREGAR EVENTO
            # ==========================================

            # Añadimos el evento al mensaje que se enviará
            # posteriormente a Telegram.
            texto += (
                f"\n\n📌 {titulo}"
                f"\n🗓️ {fecha_formateada}"
                f"\n⏰ {hora_inicio_formateada} - "
                f"{hora_fin_formateada}"
            )


            # ==========================================
            # UBICACIÓN
            # ==========================================

            # Si el evento tiene una ubicación, la agregamos.
            if evento.get("ubicacion"):

                texto += (
                    f"\n📍 {evento['ubicacion']}"
                )


            # ==========================================
            # DESCRIPCIÓN
            # ==========================================

            # Si el evento tiene descripción, también
            # la mostramos.
            if evento.get("descripcion"):

                texto += (
                    f"\n📝 {evento['descripcion']}"
                )


        # Enviamos todos los eventos al usuario.
        await update.message.reply_text(
            texto
        )

        return

        # ==========================================
    # CONSULTAR HORAS LIBRES
    # ==========================================

    # Comprobamos si Gemini determinó que el usuario
    # quiere saber qué horarios están disponibles.
    if accion.accion == "consultar_horas_libres":

        try:

            # Consultamos a Google Apps Script para obtener
            # los intervalos de tiempo que están libres.
            resultado = consultar_horas_libres(
                accion.fecha_inicio,
                accion.fecha_fin
            )

        except Exception as e:

            # Si ocurre algún error, lo mostramos en consola.
            print(
                "Error consultando horas libres:",
                e
            )

            await update.message.reply_text(
                "❌ No pude consultar las horas libres."
            )

            return


        # Comprobamos que la respuesta de Apps Script
        # haya sido correcta.
        if resultado.get("estado") != "ok":

            print(
                "Error Apps Script:",
                resultado
            )

            await update.message.reply_text(
                "❌ Hubo un error consultando "
                "las horas libres."
            )

            return


        # Obtenemos la información de disponibilidad.
        disponibilidad = resultado.get(
            "disponibilidad",
            []
        )


        # Creamos una lista vacía donde reuniremos todos
        # los horarios libres.
        horarios = []


        # Recorremos cada día de la disponibilidad.
        for dia in disponibilidad:

            # Añadimos los horarios libres encontrados
            # en ese día a nuestra lista general.
            horarios.extend(
                dia.get(
                    "horas_libres",
                    []
                )
            )
            
         

        # Si no encontramos ningún horario disponible,
        # informamos al usuario.
        if not horarios:

            await update.message.reply_text(
                "📅 No encontré horas libres "
                "en ese periodo."
            )

            return


        # ==========================================
        # CONSTRUIR RESPUESTA
        # ==========================================

        # Encabezado del mensaje.
        texto = "🕐 Horas libres:"


        # Recorremos cada intervalo disponible.
        for horario in horarios:

            # Obtenemos la hora inicial.
            hora_inicio = horario.get(
                "inicio",
                ""
            )

            # Obtenemos la hora final.
            hora_fin = horario.get(
                "fin",
                ""
            )


            # Convertimos ambas horas a formato AM/PM.
            hora_inicio_formateada = formatear_hora(
                hora_inicio
            )

            hora_fin_formateada = formatear_hora(
                hora_fin
            )


            # Añadimos el intervalo al mensaje.
            #
            # Ejemplo:
            #
            # 🟢 2:00 PM - 4:00 PM
            texto += (
                f"\n\n🟢 {hora_inicio_formateada}"
                f" - {hora_fin_formateada}"
            )


        # Enviamos los horarios disponibles al usuario.
        await update.message.reply_text(
            texto
        )

        return


    # ==========================================
    # ACCIÓN NO IMPLEMENTADA
    # ==========================================

    # Si Gemini devuelve una acción que nuestro programa
    # todavía no tiene implementada, mostramos cuál fue.
    #
    # Esto sirve principalmente para detectar nuevas acciones
    # que la IA pueda interpretar pero que el bot todavía
    # no sabe ejecutar.
    await update.message.reply_text(
        f"Entendí la acción: {accion.accion}"
    )


# ============================================================
# COMANDO DE PRUEBA
# ============================================================

async def crear_evento_prueba(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    # Esta función está asociada al comando /evento.
    #
    # Actualmente no crea ningún evento.
    #
    # Simplemente informa al usuario que la función de prueba
    # ya no es necesaria.
    #
    # Se conserva porque forma parte del código actual.
    await update.message.reply_text(
        "Esta función de prueba ya no es necesaria."
    )


# ============================================================
# FUNCIÓN PRINCIPAL DEL PROGRAMA
# ============================================================

def main():

    # Mensaje para indicar en la consola que el programa
    # está comenzando.
    print("Iniciando bot...")


    # ========================================================
    # CREAR APLICACIÓN DE TELEGRAM
    # ========================================================

    # ApplicationBuilder construye la aplicación del bot.
    #
    # .token(TOKEN) le entrega a Telegram el token que
    # identifica nuestro bot.
    #
    # .build() termina de construir la aplicación.
    #
    # En palabras sencillas:
    # aquí estamos "encendiendo" la estructura principal
    # que permitirá que Python se comunique con Telegram.
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .build()
    )


    # ========================================================
    # REGISTRAR COMANDO /START
    # ========================================================

    # Le indicamos al bot:
    #
    # "Si alguien escribe /start, ejecuta la función start".
    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )


    # ========================================================
    # REGISTRAR MENSAJES NORMALES
    # ========================================================

    # Este manejador captura mensajes de texto normales.
    #
    # filters.TEXT:
    # solamente acepta mensajes de texto.
    #
    # ~filters.COMMAND:
    # excluye comandos como /start.
    #
    # Por lo tanto, mensajes como:
    #
    # "Agenda una reunión mañana"
    #
    # serán enviados a:
    #
    # responder()
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            responder
        )
    )


    # ========================================================
    # REGISTRAR COMANDO /EVENTO
    # ========================================================

    # Registra el comando /evento y hace que ejecute
    # crear_evento_prueba().
    app.add_handler(
        CommandHandler(
            "evento",
            crear_evento_prueba
        )
    )


    # Mensaje informativo en la consola.
    print("🤖 Bot iniciado...")


    # ========================================================
    # INICIAR BOT
    # ========================================================

    # run_polling() inicia el bot y hace que Python consulte
    # continuamente a Telegram para saber si llegaron nuevos
    # mensajes.
    #
    # En palabras sencillas:
    #
    # es como si el bot estuviera diciendo constantemente:
    #
    # "¿Llegó algún mensaje?"
    # "¿Llegó algún mensaje?"
    # "¿Llegó algún mensaje?"
    #
    # Mientras este proceso esté ejecutándose, el bot
    # permanece activo.
    app.run_polling()


# ============================================================
# PUNTO DE ENTRADA DEL PROGRAMA
# ============================================================

# Esta condición comprueba si este archivo fue ejecutado
# directamente por Python.
#
# Si ejecutamos:
#
# python main.py
#
# entonces __name__ será "__main__" y se ejecutará main().
#
# Si este archivo fuera importado desde otro archivo,
# main() no se ejecutaría automáticamente.
if __name__ == "__main__":

    main()