# ============================================================
# IMPORTACIONES
# ============================================================

# Importamos desde nuestro archivo config.py las dos variables
# relacionadas con Gemini:
#
# GEMINI_API_KEY:
# Es la "llave" que permite que nuestro programa se identifique
# ante la API de Google Gemini.
#
# GEMINI_MODEL:
# Indica qué modelo de Gemini queremos utilizar.
#
# 🧠 En plastilina:
# config.py funciona como una pequeña "caja" donde guardamos
# configuraciones importantes del proyecto para no tener que
# escribirlas directamente aquí.
from config import GEMINI_API_KEY, GEMINI_MODEL


# Importamos la librería oficial de Google para poder comunicarnos
# con los modelos de inteligencia artificial Gemini.
#
# 🧠 En plastilina:
# Esta librería es como el "teléfono" que utiliza nuestro programa
# para poder hablar con Gemini.
from google import genai


# Importamos la clase Accion desde models.py.
#
# Accion representa la estructura de datos que utilizamos para
# almacenar lo que Gemini entendió del mensaje del usuario.
#
# Por ejemplo:
#
# "Agenda una reunión mañana a las 10"
#
# Gemini puede convertirlo en datos como:
#
# accion = crear_evento
# titulo = reunión
# fecha = 2026-08-20
# hora_inicio = 10:00
# hora_fin = 11:00
#
# 🧠 En plastilina:
# Accion es como una "ficha" con diferentes casillas donde
# guardamos toda la información del evento o consulta.
from models import Accion


# Importamos datetime para poder conocer la fecha actual.
#
# Esto es necesario para que Gemini pueda interpretar expresiones
# como:
#
# "hoy"
# "mañana"
# "el próximo lunes"
# "el martes de la próxima semana"
from datetime import datetime


# Importamos json para trabajar con información en formato JSON.
#
# Gemini devuelve la información estructurada como JSON y Python
# necesita convertir ese texto en datos que pueda utilizar.
#
# 🧠 En plastilina:
# JSON es una forma ordenada de empaquetar información para que
# diferentes programas puedan entenderla.
import json


# ============================================================
# CONFIGURACIÓN GEMINI
# ============================================================

# Comprobamos que realmente exista una clave API de Gemini.
#
# Si GEMINI_API_KEY está vacío o no existe, detenemos el programa
# inmediatamente mostrando un error.
#
# 🧠 En plastilina:
# Antes de intentar llamar a Gemini, comprobamos que tengamos
# la "llave" necesaria para entrar.
if not GEMINI_API_KEY:

    raise ValueError(
        "No se encontró GEMINI_API_KEY en el archivo .env"
    )


# Creamos el cliente de Gemini.
#
# El cliente es el objeto que posteriormente utilizaremos para
# enviarle instrucciones a Gemini y recibir sus respuestas.
#
# Le entregamos nuestra API Key para que Google pueda identificar
# y autorizar las solicitudes.
#
# 🧠 En plastilina:
# Aquí estamos diciendo:
#
# "Gemini, este programa tiene esta llave y quiere comunicarse
# contigo."
client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# LIMPIAR JSON
# ============================================================

# Esta función recibe el texto que devuelve Gemini y lo limpia
# antes de intentar convertirlo en JSON.
#
# 🧠 En plastilina:
# Gemini normalmente debería devolver solamente el JSON que
# necesitamos, pero algunas veces puede envolverlo en algo como:
#
# ```json
# {
#     ...
# }
# ```
#
# Esta función quita esas "envolturas" para dejar solamente
# el contenido JSON.
def limpiar_json(texto):


    # Eliminamos espacios y saltos de línea innecesarios
    # que puedan existir al principio o al final del texto.
    texto = texto.strip()


    # Comprobamos si la respuesta comienza con ``` .
    #
    # Esto normalmente significa que Gemini devolvió el JSON
    # dentro de un bloque de Markdown.
    if texto.startswith("```"):


        # Eliminamos la etiqueta ```json si existe.
        texto = texto.replace("```json", "")


        # Eliminamos también los ``` restantes.
        texto = texto.replace("```", "")


    # Volvemos a eliminar espacios innecesarios y devolvemos
    # el texto limpio.
    return texto.strip()


# ============================================================
# APLICAR VALORES PREDETERMINADOS
# ============================================================

# Esta función se encarga de colocar determinados valores
# automáticamente cuando Gemini no los proporciona.
#
# Actualmente se utiliza principalmente para las horas
# predeterminadas de los eventos.
#
# 🧠 En plastilina:
# Es como una pequeña "red de seguridad".
#
# Si el usuario dice:
#
# "Agenda una reunión mañana"
#
# y no proporciona una hora, nosotros decidimos que por defecto
# será de 12:00 PM a 1:00 PM.
def aplicar_valores_predeterminados(datos):


    # --------------------------------------------------------
    # SOLAMENTE PARA CREAR EVENTOS
    # --------------------------------------------------------

    # Comprobamos que la acción solicitada sea crear_evento.
    #
    # Esto es importante porque las horas predeterminadas
    # solamente tienen sentido cuando estamos creando un evento.
    if datos.get("accion") == "crear_evento":


        # Si Gemini no encontró una hora de inicio,
        # establecemos las 12:00 del mediodía.
        #
        # .get("hora_inicio") intenta obtener ese dato.
        # Si está vacío, entra en este if.
        if not datos.get("hora_inicio"):

            datos["hora_inicio"] = "12:00"


        # Si Gemini no encontró una hora de finalización,
        # establecemos la 1:00 PM.
        #
        # De esta manera, cuando el usuario solamente indica
        # una hora de inicio, el evento tiene una duración
        # predeterminada de una hora.
        if not datos.get("hora_fin"):

            datos["hora_fin"] = "13:00"


        # ----------------------------------------------------
        # Las horas NUNCA deben quedar como faltantes
        # ----------------------------------------------------

        # Reconstruimos la lista de información faltante.
        #
        # Recorremos todos los campos que Gemini haya colocado
        # en "faltantes" y eliminamos:
        #
        # - hora_inicio
        # - hora_fin
        #
        # porque nuestro programa puede completar esas horas
        # automáticamente.
        #
        # 🧠 En plastilina:
        # Aunque Gemini diga "me falta la hora", nosotros le
        # respondemos:
        #
        # "No pasa nada, nosotros tenemos una hora por defecto."
        datos["faltantes"] = [
            campo
            for campo in datos.get("faltantes", [])
            if campo not in [
                "hora_inicio",
                "hora_fin"
            ]
        ]


    # Devolvemos los datos después de aplicar las modificaciones.
    return datos


# ============================================================
# INTERPRETAR MENSAJE
# ============================================================

# Esta es una de las funciones principales del sistema.
#
# Recibe directamente el mensaje que escribió el usuario
# en Telegram y se lo entrega a Gemini junto con todas
# las instrucciones necesarias para interpretarlo.
#
# Por ejemplo:
#
# "Agenda una reunión mañana a las 10"
#
# Gemini debe determinar:
#
# - qué acción realizar
# - qué título tiene
# - qué fecha corresponde
# - qué hora tiene
# - si se repite
# - si tiene recordatorios
# - etc.
def interpretar_mensaje(mensaje: str):


    # Obtenemos la fecha actual del ordenador donde se está
    # ejecutando el bot.
    #
    # El formato utilizado será:
    #
    # YYYY-MM-DD
    #
    # Ejemplo:
    #
    # 2026-08-19
    #
    # 🧠 En plastilina:
    # Le damos a Gemini un "reloj/calendario de referencia"
    # para que pueda entender palabras como "mañana".
    fecha_actual = datetime.now().strftime("%Y-%m-%d")


    # ========================================================
    # PROMPT PARA GEMINI
    # ========================================================
    #
    # Aquí construimos las instrucciones que recibirá Gemini.
    #
    # La letra f antes de las comillas permite insertar variables
    # de Python dentro del texto.
    #
    # En este caso insertamos:
    #
    # {fecha_actual}
    # {mensaje}
    #
    # 🧠 En plastilina:
    # Este prompt es como el "manual de instrucciones" que le
    # entregamos a Gemini antes de pedirle que interprete
    # lo que escribió el usuario.
    prompt = f"""
Eres un asistente personal de agenda.

Tu trabajo es interpretar las solicitudes del usuario relacionadas
con su calendario.

FECHA ACTUAL:

{fecha_actual}


==================================================
ACCIONES DISPONIBLES
==================================================

Solamente existen estas acciones:

1. crear_evento
2. consultar_eventos
3. consultar_horas_libres


==================================================
CREAR EVENTOS
==================================================

Ejemplo:

"Agenda cita con María mañana de 10 am a 12 pm"

Debe producir algo como:

{{
    "accion": "crear_evento",
    "titulo": "Cita con María",
    "fecha": "AAAA-MM-DD",
    "hora_inicio": "10:00",
    "hora_fin": "12:00",
    "descripcion": "",
    "ubicacion": "",
    "repeticion": "",
    "fecha_fin_repeticion": "",
    "recordatorios_dias": [],
    "fecha_inicio": "",
    "fecha_fin": "",
    "filtro_titulo": "",
    "faltantes": []
}}


==================================================
HORAS PREDETERMINADAS
==================================================

La hora NO es obligatoria.

Si el usuario NO indica ninguna hora:

"hora_inicio": "12:00"
"hora_fin": "13:00"

Es decir, el evento se agenda automáticamente
de 12:00 del mediodía a 13:00.

IMPORTANTE:

Nunca agregues "hora_inicio" ni "hora_fin"
a "faltantes".

Si el usuario indica solamente una hora de inicio,
utiliza esa hora como "hora_inicio" y establece
"hora_fin" una hora después.

Ejemplo:

"Agenda examen mañana a las 10"

Resultado:

"hora_inicio": "10:00"
"hora_fin": "11:00"


==================================================
EVENTOS SEMANALES
==================================================

Si el usuario dice:

"Investigación de Operaciones todos los martes
hasta el 7 de diciembre de 10 am a 12 pm"

usa:

"repeticion": "semanal"

y:

"fecha_fin_repeticion": "2026-12-07"

La fecha corresponde al primer evento.


==================================================
EVENTOS MENSUALES
==================================================

Si el usuario dice:

"Programa los 24 de cada mes el pago de 28 mil pesos a Juli"

usa:

"repeticion": "mensual"

La fecha debe ser el primer día 24 disponible
a partir de la fecha actual.


==================================================
DESCRIPCIONES
==================================================

Información adicional como:

- aula
- profesor
- monto
- persona
- concepto
- instrucciones
- detalles del pago

debe ir en "descripcion".


Ejemplo:

"Agendar Investigación de Operaciones todos los martes
hasta el 7 de diciembre de 10 am a 12 pm y será en el aula P-17 204"

puede producir:

"descripcion": "Aula P-17 204"


Para pagos:

"pagar 28000 pesos a Juli"

debe producir:

"descripcion": "Pago de 28000 pesos a Juli"


Si el usuario indica explícitamente una ubicación,
también puede utilizarse:

"ubicacion"


==================================================
RECORDATORIOS
==================================================

El usuario puede pedir varios recordatorios.

Ejemplo:

"Notifícame 2 semanas antes y 1 semana antes"

debe convertirse en:

"recordatorios_dias": [14, 7]


Ejemplo:

"Notifícame 3 días antes"

debe convertirse en:

"recordatorios_dias": [3]


Conversiones:

1 semana = 7 días
2 semanas = 14 días
3 semanas = 21 días

1 día = 1 día
3 días = 3 días


NO conviertas los recordatorios en horas.

Siempre utiliza cantidades de días.

==================================================
CONSULTAR HORAS LIBRES
==================================================

Si el usuario pregunta por sus horarios disponibles
o sus horas libres, utiliza:

"accion": "consultar_horas_libres"


Ejemplos:

"¿Qué horas libres tengo mañana?"

"¿Qué horas tengo disponibles mañana?"

"¿Qué horarios tengo libres el martes de la próxima semana?"

"¿Cuándo estoy libre el viernes?"


En estos casos establece:

"fecha_inicio": fecha correspondiente al día solicitado

"fecha_fin": la misma fecha


Ejemplo:

Si mañana es 2026-08-20:

{{
    "accion": "consultar_horas_libres",
    "fecha_inicio": "2026-08-20",
    "fecha_fin": "2026-08-20"
}}


IMPORTANTE:

La IA solamente debe determinar
qué fecha quiere consultar.

NO debe calcular las horas libres.

Las horas libres serán calculadas posteriormente
consultando directamente Google Calendar.


Si el usuario solicita un día específico,
utiliza ese día.

Si dice:

"el martes de la próxima semana"

calcula correctamente la fecha de ese martes
utilizando la fecha actual.


Las fechas siempre deben tener:

YYYY-MM-DD


==================================================
CONSULTAR EVENTOS
==================================================

Si el usuario pregunta:

"¿Qué tengo mañana?"

usa:

"accion": "consultar_eventos"

y establece:

"fecha_inicio": fecha de mañana
"fecha_fin": fecha de mañana


Si pregunta:

"¿Qué tengo hoy?"

usa la fecha actual.


Si pregunta:

"¿Qué tengo esta semana?"

consulta desde el lunes de la semana actual
hasta el domingo de la semana actual.


Si pregunta:

"¿Qué tengo la otra semana?"

consulta la semana siguiente a la semana actual.


==================================================
PREGUNTAS SOBRE UNA MATERIA
==================================================

Si el usuario pregunta:

"¿En qué aula tengo Investigación de Operaciones hoy?"

usa:

"accion": "consultar_eventos"

y establece el rango correspondiente a hoy.

Además establece:

"filtro_titulo": "Investigación de Operaciones"


Esto permitirá buscar únicamente eventos
relacionados con esa materia.


==================================================
FECHAS
==================================================

Nunca inventes información.

Si el usuario dice:

- hoy
- mañana
- pasado mañana
- este lunes
- este martes
- próximo lunes
- la próxima semana
- la otra semana

calcula correctamente las fechas utilizando:

{fecha_actual}


Si no indica año,
utiliza el año correspondiente.


Las fechas siempre deben tener:

YYYY-MM-DD


==================================================
INFORMACIÓN FALTANTE
==================================================

Para crear un evento son necesarios:

- título
- fecha

La hora NO es obligatoria.

Si no existe hora:

hora_inicio = 12:00
hora_fin = 13:00


NUNCA agregues:

"hora_inicio"

ni:

"hora_fin"

a "faltantes".


Si falta el título o la fecha,
agrégalos a:

"faltantes"


==================================================
FORMATO DE RESPUESTA
==================================================

Devuelve ÚNICAMENTE JSON válido.

Nunca utilices Markdown.

La estructura exacta debe ser:

{{
    "accion": "",
    "titulo": "",
    "fecha": "",
    "hora_inicio": "",
    "hora_fin": "",
    "descripcion": "",
    "ubicacion": "",
    "repeticion": "",
    "fecha_fin_repeticion": "",
    "recordatorios_dias": [],
    "fecha_inicio": "",
    "fecha_fin": "",
    "filtro_titulo": "",
    "faltantes": []
}}


MENSAJE DEL USUARIO:

{mensaje}
"""


    # ========================================================
    # ENVIAR EL PROMPT A GEMINI
    # ========================================================

    # Enviamos el prompt al modelo de Gemini que configuramos
    # anteriormente.
    #
    # generate_content() significa básicamente:
    #
    # "Gemini, aquí tienes estas instrucciones y este mensaje.
    # Dame una respuesta."
    respuesta = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )


    # Mostramos en la consola exactamente lo que respondió Gemini.
    #
    # Esto es muy útil durante el desarrollo porque podemos ver
    # qué interpretación hizo la IA antes de que Python procese
    # la respuesta.
    print("RESPUESTA GEMINI:")
    print(respuesta.text)


    # Pasamos la respuesta de Gemini por nuestra función
    # de limpieza.
    #
    # Esto elimina posibles ```json y otros elementos que
    # impedirían interpretar correctamente el JSON.
    texto = limpiar_json(
        respuesta.text
    )


    # Mostramos en consola el resultado después de limpiarlo.
    print("TEXTO LIMPIO:")
    print(texto)


    # Convertimos el texto JSON en un objeto/diccionario de Python.
    #
    # 🧠 En plastilina:
    #
    # Gemini nos entrega información como texto.
    #
    # json.loads() convierte ese texto en algo que Python
    # puede manipular directamente.
    #
    # Por ejemplo:
    #
    # '{"titulo":"Reunión"}'
    #
    # pasa a ser algo parecido a:
    #
    # {"titulo": "Reunión"}
    datos = json.loads(texto)


    # Aplicamos los valores predeterminados que definimos
    # anteriormente.
    #
    # Por ejemplo, si no existe una hora, se agregará:
    #
    # 12:00 → 13:00
    datos = aplicar_valores_predeterminados(
        datos
    )


    # Mostramos en consola los datos finales después
    # de aplicar las reglas adicionales.
    print("DATOS FINALES:")
    print(datos)


    # Convertimos el diccionario de Python en un objeto
    # de tipo Accion.
    #
    # Esto permite que el resto del programa pueda trabajar
    # con propiedades como:
    #
    # accion.titulo
    # accion.fecha
    # accion.hora_inicio
    #
    # en lugar de trabajar directamente con un diccionario.
    #
    # 🧠 En plastilina:
    # Primero Gemini entrega una "caja" con datos.
    # Aquí convertimos esa caja en una estructura organizada
    # que nuestro programa conoce y sabe utilizar.
    return Accion(**datos)


# ============================================================
# COMPLETAR INFORMACIÓN
# ============================================================

# Esta función se utiliza cuando el usuario inició una solicitud
# pero le faltó algún dato.
#
# Por ejemplo:
#
# Usuario:
# "Agenda una reunión"
#
# El bot puede detectar que falta la fecha.
#
# Después el usuario responde:
#
# "Mañana"
#
# Esta función toma la solicitud anterior y la nueva respuesta
# para completar la información pendiente.
#
# 🧠 En plastilina:
# Es como si el bot tuviera una conversación pendiente:
#
# "Me dijiste que quieres crear una reunión,
# pero todavía necesito saber cuándo."
#
# Usuario:
# "Mañana."
#
# Esta función junta ambas partes.
def completar_informacion(
    accion_actual: Accion,
    respuesta_usuario: str
):


    # Obtenemos nuevamente la fecha actual.
    #
    # Esto permite interpretar respuestas relativas como:
    #
    # "mañana"
    # "el viernes"
    # "la próxima semana"
    fecha_actual = datetime.now().strftime("%Y-%m-%d")


    # ========================================================
    # CREAR PROMPT PARA COMPLETAR LA SOLICITUD
    # ========================================================

    # Construimos las instrucciones que recibirá Gemini.
    #
    # En este caso le proporcionamos:
    #
    # - la fecha actual
    # - la solicitud que estaba pendiente
    # - la nueva respuesta del usuario
    #
    # De esta manera Gemini tiene el contexto necesario para
    # completar la información.
    prompt = f"""
Eres un asistente personal completando
una solicitud pendiente.


FECHA ACTUAL:

{fecha_actual}


==================================================
SOLICITUD ACTUAL
==================================================

{accion_actual.model_dump_json(indent=2)}


==================================================
RESPUESTA DEL USUARIO
==================================================

"{respuesta_usuario}"


==================================================
OBJETIVO
==================================================

Completa únicamente la información que falta.


==================================================
REGLAS
==================================================

1. Mantén exactamente la misma acción.


2. Mantén el título existente.


3. No borres información existente.


4. No inventes información.


5. Si el usuario proporciona una fecha relativa,
calcula la fecha usando la fecha actual.


6. Convierte fechas a:

YYYY-MM-DD


7. Convierte horas a:

HH:MM


8. Si el usuario proporciona recordatorios:

"2 semanas antes" → 14
"1 semana antes" → 7
"3 días antes" → 3


9. La hora NO es obligatoria.


10. Si el evento no tiene hora:

hora_inicio = "12:00"
hora_fin = "13:00"


11. Si el usuario proporciona solamente
una hora de inicio:

hora_inicio = hora indicada

hora_fin = una hora después


12. NUNCA agregues hora_inicio
ni hora_fin a "faltantes".


13. Si falta título o fecha,
sí deben permanecer en "faltantes".


==================================================
FORMATO
==================================================

Devuelve únicamente JSON válido.

No utilices Markdown.

{{
    "accion": "",
    "titulo": "",
    "fecha": "",
    "hora_inicio": "",
    "hora_fin": "",
    "descripcion": "",
    "ubicacion": "",
    "repeticion": "",
    "fecha_fin_repeticion": "",
    "recordatorios_dias": [],
    "fecha_inicio": "",
    "fecha_fin": "",
    "filtro_titulo": "",
    "faltantes": []
}}
"""


    # Enviamos las instrucciones a Gemini.
    #
    # En este caso estamos utilizando nuevamente el mismo modelo
    # configurado en GEMINI_MODEL.
    respuesta = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt
    )


    # Mostramos en consola la respuesta original de Gemini.
    #
    # El texto "COMPLETANDO" nos permite distinguirla de la
    # respuesta generada por interpretar_mensaje().
    print("RESPUESTA GEMINI COMPLETANDO:")
    print(respuesta.text)


    # Limpiamos la respuesta por si Gemini utilizó Markdown
    # alrededor del JSON.
    texto = limpiar_json(
        respuesta.text
    )


    # Mostramos el JSON después de limpiarlo.
    print("TEXTO LIMPIO COMPLETANDO:")
    print(texto)


    # Convertimos el JSON en un diccionario de Python.
    datos = json.loads(texto)


    # Aplicamos nuevamente nuestros valores predeterminados.
    #
    # Esto es importante porque, después de completar la
    # información, todavía podría faltar una hora.
    datos = aplicar_valores_predeterminados(
        datos
    )


    # Mostramos el resultado final en la consola.
    print("DATOS FINALES COMPLETANDO:")
    print(datos)


    # Finalmente convertimos los datos en un objeto Accion
    # para que el resto del bot pueda trabajar con ellos.
    return Accion(**datos)