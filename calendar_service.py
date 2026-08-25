import os
import requests

from dotenv import load_dotenv


# ==========================================
# CARGAR VARIABLES DE ENTORNO
# ==========================================

# Carga las variables guardadas en el archivo .env.
#
# En "plastilina":
# El archivo .env funciona como una pequeña caja donde
# guardamos información de configuración que no queremos
# escribir directamente dentro del código.
#
# Por ejemplo:
#
# URL_APPS_SCRIPT=https://script.google.com/...
#
# Así, el código puede obtener esa información
# sin tener que escribir la URL directamente aquí.
load_dotenv()


# Obtiene del archivo .env la URL de nuestro
# Google Apps Script.
#
# Esta URL es la "dirección" a la que nuestro bot
# enviará las instrucciones para trabajar con Google Calendar.
URL_APPS_SCRIPT = os.getenv("URL_APPS_SCRIPT")


# ==========================================
# FUNCIÓN AUXILIAR
# ==========================================

def enviar_apps_script(datos):

    """
    Envía una petición POST a Google Apps Script.

    Google Apps Script normalmente responde primero
    con un HTTP 302 y una URL de googleusercontent.

    IMPORTANTE:
    La petición original es POST, pero al seguir la
    redirección de Apps Script debemos hacer GET.
    """

    # Verificamos que realmente exista la URL
    # de Google Apps Script.
    #
    # En "plastilina":
    # Antes de intentar enviar una carta,
    # comprobamos que tengamos la dirección de destino.
    if not URL_APPS_SCRIPT:

        raise Exception(
            "No existe URL_APPS_SCRIPT en el archivo .env"
        )


    # Mostramos en la consola exactamente qué información
    # estamos a punto de enviar a Google Apps Script.
    #
    # Esto es muy útil durante las pruebas porque nos permite
    # ver qué está haciendo realmente el bot.
    print("Enviando a Apps Script:")
    print(datos)


    # Indicamos que los datos que estamos enviando
    # tienen formato JSON.
    #
    # JSON es simplemente una forma organizada de
    # empaquetar información para que dos programas
    # puedan entenderse entre sí.
    headers = {
        "Content-Type": "application/json"
    }


    # ==========================================
    # PRIMERA PETICIÓN
    # ==========================================

    # Enviamos una petición POST a Google Apps Script.
    #
    # POST significa, simplificando:
    # "Aquí tienes estos datos, haz algo con ellos".
    #
    # "json=datos":
    # convierte nuestro diccionario de Python
    # en información JSON.
    #
    # "headers=headers":
    # le informa al servidor que estamos enviando JSON.
    #
    # "allow_redirects=False":
    # evita que requests siga automáticamente
    # la redirección de Google Apps Script.
    #
    # Esto es importante porque queremos controlar
    # manualmente esa redirección.
    #
    # "timeout=30":
    # evita que el programa se quede esperando
    # indefinidamente si Google no responde.
    respuesta = requests.post(
        URL_APPS_SCRIPT,
        json=datos,
        headers=headers,
        allow_redirects=False,
        timeout=30
    )


    # Mostramos en consola el código HTTP que devolvió
    # Google Apps Script en la primera respuesta.
    #
    # Por ejemplo:
    #
    # 302 = Google quiere redirigirnos a otra URL.
    #
    # En nuestro caso, el 302 es normal y forma parte
    # del funcionamiento de Google Apps Script como
    # aplicación web.
    print(
        "Código respuesta inicial:",
        respuesta.status_code
    )


    # ==========================================
    # MANEJAR REDIRECCIÓN DE APPS SCRIPT
    # ==========================================

    # Comprobamos si Google respondió con alguno
    # de estos códigos de redirección.
    #
    # En "plastilina":
    # Google nos está diciendo:
    #
    # "La respuesta no está aquí,
    # ve a esta otra dirección".
    #
    # 301, 302, 303, 307 y 308 son diferentes
    # tipos de redirecciones HTTP.
    if respuesta.status_code in (301, 302, 303, 307, 308):

        # Obtenemos la dirección a la que Google
        # quiere que vayamos.
        #
        # Esa dirección viene dentro de la cabecera
        # HTTP llamada "Location".
        nueva_url = respuesta.headers.get("Location")


        # Si Google indicó una redirección pero no
        # nos dio la dirección de destino,
        # no podemos continuar.
        if not nueva_url:

            return {
                "estado": "error",
                "mensaje": (
                    "Apps Script respondió con una "
                    "redirección pero no indicó la URL destino."
                )
            }


        # Mostramos en consola la nueva dirección
        # proporcionada por Google.
        print("Redirección detectada:")
        print(nueva_url)


        # ==========================================
        # IMPORTANTE
        #
        # NO HACER POST A LA URL REDIRIGIDA.
        #
        # Google Apps Script espera que sigamos
        # la redirección con GET.
        # ==========================================

        # Ahora hacemos una petición GET a la nueva URL.
        #
        # En "plastilina":
        # Primero tocamos la puerta principal de Google.
        # Google nos dice:
        #
        # "La respuesta está en esta otra puerta".
        #
        # Entonces vamos a esa segunda puerta
        # mediante GET para obtener finalmente
        # la respuesta.
        respuesta = requests.get(
            nueva_url,
            timeout=30
        )


    # ==========================================
    # INFORMACIÓN FINAL
    # ==========================================

    # Mostramos el código HTTP de la respuesta final.
    #
    # Lo normal cuando todo salió correctamente
    # es obtener:
    #
    # 200 = OK
    print(
        "Código respuesta final:",
        respuesta.status_code
    )


    # Mostramos la URL donde terminó finalmente
    # la petición.
    print(
        "URL final:",
        respuesta.url
    )


    # Indicamos en la consola que a continuación
    # vamos a mostrar la respuesta que nos dio
    # Google Apps Script.
    print(
        "Respuesta Apps Script:"
    )


    # Imprimimos literalmente el contenido de la respuesta.
    #
    # Por ejemplo:
    #
    # {"estado":"ok","evento":"Pago a Juli"}
    print(
        respuesta.text
    )


    # ==========================================
    # VALIDAR HTTP
    # ==========================================

    # Comprobamos que Google haya respondido
    # correctamente.
    #
    # El código 200 significa:
    #
    # "La petición fue procesada correctamente".
    if respuesta.status_code != 200:

        # Si recibimos otro código,
        # devolvemos un error al resto del programa.
        return {
            "estado": "error",
            "mensaje": (
                "Apps Script respondió con "
                f"código HTTP {respuesta.status_code}"
            )
        }


    # ==========================================
    # LEER JSON
    # ==========================================

    # Intentamos convertir la respuesta de Google
    # desde texto JSON a un diccionario de Python.
    #
    # En "plastilina":
    # Google nos entrega una cajita con información.
    # Aquí abrimos esa cajita para que Python
    # pueda trabajar con lo que hay dentro.
    try:

        resultado = respuesta.json()

        return resultado


    # Si la respuesta no tiene un JSON válido,
    # capturamos el error y devolvemos un mensaje
    # controlado en lugar de romper todo el bot.
    except Exception:

        return {
            "estado": "error",
            "mensaje": (
                "Apps Script no devolvió "
                "una respuesta JSON válida."
            )
        }


# ==========================================
# CREAR EVENTO
# ==========================================

def crear_evento(accion):

    # Creamos un diccionario con la información
    # necesaria para crear un evento en Google Calendar.
    #
    # "accion" contiene la información que previamente
    # interpretó Gemini.
    #
    # Por ejemplo:
    #
    # accion.titulo = "Pago a Juli"
    # accion.fecha = "2026-08-24"
    # accion.hora_inicio = "12:00"
    #
    # En "plastilina":
    # Aquí tomamos la información que nos dio la IA
    # y la empacamos en una caja para enviársela
    # a Google Apps Script.
    datos = {

        # Le indicamos a Apps Script qué operación
        # queremos realizar.
        "accion": "crear_evento",

        # Título del evento.
        "titulo": accion.titulo,

        # Fecha del evento.
        "fecha": accion.fecha,

        # Hora en la que comienza.
        "hora_inicio": accion.hora_inicio,

        # Hora en la que termina.
        "hora_fin": accion.hora_fin,

        # Descripción adicional del evento.
        "descripcion": accion.descripcion,

        # Lugar del evento.
        "ubicacion": accion.ubicacion,

        # Tipo de repetición.
        #
        # Puede estar vacío, ser "semanal"
        # o "mensual".
        "repeticion": accion.repeticion,

        # Fecha hasta la que debe repetirse,
        # si corresponde.
        "fecha_fin_repeticion": (
            accion.fecha_fin_repeticion
        ),

        # Lista de recordatorios expresados
        # en cantidad de días.
        #
        # Ejemplo:
        # [3] = 3 días antes.
        "recordatorios_dias": (
            accion.recordatorios_dias
        )
    }


    # Mostramos en consola la información que vamos
    # a utilizar para crear el evento.
    print("Creando evento:")
    print(datos)


    # Enviamos los datos a Google Apps Script
    # utilizando nuestra función auxiliar.
    #
    # Así no tenemos que repetir toda la lógica
    # de conexión cada vez que queramos comunicarnos
    # con Apps Script.
    return enviar_apps_script(
        datos
    )


# ==========================================
# CONSULTAR EVENTOS
# ==========================================

def consultar_eventos(
    fecha_inicio,
    fecha_fin,
    filtro_titulo=""
):

    # Preparamos los datos necesarios para solicitar
    # eventos existentes en Google Calendar.
    datos = {

        # Le indicamos a Apps Script qué queremos hacer.
        "accion": "consultar_eventos",

        # Fecha inicial del periodo que queremos consultar.
        "fecha_inicio": fecha_inicio,

        # Fecha final del periodo.
        "fecha_fin": fecha_fin,

        # Si se especifica un título,
        # Apps Script puede utilizarlo para filtrar.
        #
        # Si no hay filtro, queda como texto vacío.
        "filtro_titulo": filtro_titulo
    }


    # Mostramos en consola la información
    # que vamos a enviar.
    print("Consultando calendario:")
    print(datos)


    # Enviamos la solicitud utilizando la función
    # que maneja la comunicación con Apps Script.
    resultado = enviar_apps_script(
        datos
    )


    # Mostramos el resultado que devolvió Apps Script.
    #
    # Esto ayuda muchísimo para depurar problemas,
    # porque podemos comprobar qué recibió Python.
    print(
        "Resultado consultar eventos:"
    )


    print(
        resultado
    )


    # Devolvemos el resultado al programa principal.
    return resultado


# ==========================================
# CONSULTAR HORAS LIBRES
# ==========================================

def consultar_horas_libres(
    fecha_inicio,
    fecha_fin
):

    # Preparamos la información que necesita
    # Google Apps Script para calcular
    # qué horas están disponibles.
    datos = {

        # Indicamos que queremos consultar
        # las horas libres.
        "accion": "consultar_horas_libres",

        # Primer día que queremos consultar.
        "fecha_inicio": fecha_inicio,

        # Último día que queremos consultar.
        "fecha_fin": fecha_fin

    }


    # Mostramos en consola lo que vamos a enviar.
    print("Consultando horas libres:")

    print(datos)


    # Enviamos la petición POST directamente
    # a la URL de Google Apps Script.
    #
    # "json=datos":
    # convierte nuestro diccionario en JSON.
    #
    # "timeout=60":
    # esperamos como máximo 60 segundos.
    respuesta = requests.post(

        URL_APPS_SCRIPT,

        json=datos,

        timeout=60

    )


    # Mostramos el código HTTP de la primera respuesta.
    print(
        "Código respuesta inicial:",
        respuesta.status_code
    )


    # ==========================================
    # SEGUIR REDIRECCIÓN DE APPS SCRIPT
    # ==========================================

    # Si Google Apps Script responde con 302,
    # significa que quiere enviarnos a otra URL
    # para obtener la respuesta final.
    if respuesta.status_code == 302:

        # Extraemos la URL indicada por Google.
        url_redireccion = respuesta.headers.get(
            "Location"
        )


        # Mostramos la URL de redirección
        # para poder verla durante las pruebas.
        print(
            "Redirección detectada:"
        )


        print(
            url_redireccion
        )


        # Hacemos una petición GET a la URL
        # proporcionada por Google.
        #
        # En "plastilina":
        # Google nos dice dónde está la respuesta
        # y nosotros vamos a buscarla allí.
        respuesta = requests.get(
            url_redireccion,
            timeout=60
        )


        # Mostramos el código de la respuesta final.
        print(
            "Código respuesta final:",
            respuesta.status_code
        )


        # Mostramos la URL final donde terminamos.
        print(
            "URL final:",
            respuesta.url
        )


    # Mostramos el contenido final que devolvió
    # Google Apps Script.
    print(
        "Respuesta Apps Script:"
    )


    print(
        respuesta.text
    )


    # Intentamos convertir la respuesta JSON
    # en un diccionario de Python.
    try:

        return respuesta.json()


    # Si la respuesta no es un JSON válido,
    # devolvemos un mensaje de error controlado.
    except ValueError:

        return {

            "estado": "error",

            "mensaje":
                "Respuesta inválida de Apps Script"

        }