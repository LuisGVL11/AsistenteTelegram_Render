# Importamos Optional desde typing.
# Optional significa que un dato puede existir o puede estar vacío (None).
#
# Por ejemplo:
# titulo: Optional[str]
#
# significa:
# "titulo puede contener un texto (str), pero también puede estar vacío".
from typing import Optional


# Importamos las herramientas principales de Pydantic.
#
# BaseModel:
# Nos permite crear una estructura de datos organizada y validar
# que la información recibida tenga el formato esperado.
#
# Field:
# Permite configurar ciertos campos de nuestro modelo,
# por ejemplo, darle un valor predeterminado.
from pydantic import BaseModel, Field


# ============================================================
# MODELO DE ACCIÓN
# ============================================================
#
# Esta clase funciona como una "plantilla" para todas las órdenes
# que puede interpretar nuestro bot.
#
# En palabras sencillas:
#
# Gemini recibe algo como:
#
# "Agenda una reunión mañana a las 3"
#
# y devuelve información estructurada.
#
# Esta clase le dice al programa:
#
# "La información de una orden debe tener estos campos".
#
# Así evitamos trabajar con datos desordenados.
class Accion(BaseModel):

    # --------------------------------------------------------
    # ACCIÓN QUE DEBE REALIZAR EL BOT
    # --------------------------------------------------------
    #
    # Indica qué quiere hacer el usuario.
    #
    # Ejemplos:
    #
    # "crear_evento"
    # "consultar_eventos"
    # "consultar_horas_libres"
    #
    # Este campo es obligatorio porque el programa necesita
    # saber qué camino tomar.
    accion: str


    # --------------------------------------------------------
    # INFORMACIÓN DEL EVENTO
    # --------------------------------------------------------
    #
    # Título o nombre del evento.
    #
    # Ejemplo:
    #
    # "Reunión con María"
    #
    # Es Optional porque algunas acciones, como consultar
    # horas libres, no necesitan tener un título.
    titulo: Optional[str] = None


    # Fecha del evento.
    #
    # Normalmente se maneja con el formato:
    #
    # YYYY-MM-DD
    #
    # Ejemplo:
    #
    # "2026-08-20"
    #
    # Puede quedar vacío porque no todas las acciones
    # trabajan directamente con una fecha de evento.
    fecha: Optional[str] = None


    # Hora en la que comienza el evento.
    #
    # Se maneja normalmente en formato de 24 horas:
    #
    # "14:00"
    #
    # Aunque el usuario puede escribir:
    #
    # "2 de la tarde"
    #
    # La IA se encarga de convertirlo al formato esperado.
    hora_inicio: Optional[str] = None


    # Hora en la que termina el evento.
    #
    # Ejemplo:
    #
    # "16:00"
    #
    # Al igual que hora_inicio, puede quedar vacío.
    hora_fin: Optional[str] = None


    # --------------------------------------------------------
    # INFORMACIÓN ADICIONAL DEL EVENTO
    # --------------------------------------------------------

    # Descripción del evento.
    #
    # Puede contener información adicional como:
    #
    # "Llevar documentos"
    # "Pagar 28000 pesos a Juli"
    # "Examen del segundo corte"
    #
    # No es obligatorio.
    descripcion: Optional[str] = None


    # Ubicación física o lugar del evento.
    #
    # Ejemplo:
    #
    # "Aula P-17 204"
    # "Universidad"
    # "Oficina"
    #
    # Tampoco es obligatorio.
    ubicacion: Optional[str] = None


    # --------------------------------------------------------
    # REPETICIÓN DEL EVENTO
    # --------------------------------------------------------

    # Indica si el evento se repite.
    #
    # Ejemplos:
    #
    # "semanal"
    # "mensual"
    #
    # Si el evento no se repite, puede quedar vacío.
    repeticion: Optional[str] = None


    # Fecha hasta la cual debe repetirse el evento.
    #
    # Ejemplo:
    #
    # Si tenemos una reunión todos los martes hasta
    # el 7 de diciembre:
    #
    # "2026-12-07"
    #
    # Solo se utiliza cuando existe una repetición.
    fecha_fin_repeticion: Optional[str] = None


    # --------------------------------------------------------
    # RECORDATORIOS
    # --------------------------------------------------------
    #
    # Aquí guardamos los recordatorios expresados en días.
    #
    # Por ejemplo:
    #
    # [14, 7]
    #
    # significa:
    #
    # - Recordar 14 días antes.
    # - Recordar 7 días antes.
    #
    # list[int] significa que la lista solamente debe contener
    # números enteros.
    #
    # Field(default_factory=list) hace que, si no se proporciona
    # ningún recordatorio, el valor inicial sea una lista vacía:
    #
    # []
    #
    # En palabras sencillas:
    #
    # "Si no hay recordatorios, simplemente no hay ninguno".
    recordatorios_dias: list[int] = Field(default_factory=list)


    # --------------------------------------------------------
    # DATOS PARA CONSULTAR EVENTOS
    # --------------------------------------------------------
    #
    # Estos campos se utilizan cuando la acción es:
    #
    # "consultar_eventos"
    #
    # En lugar de representar la fecha de un evento que vamos
    # a crear, representan el rango de fechas que queremos revisar.
    #
    # Por ejemplo:
    #
    # fecha_inicio = "2026-08-20"
    # fecha_fin = "2026-08-20"
    #
    # significa:
    #
    # "Consulta los eventos del 20 de agosto".
    fecha_inicio: Optional[str] = None


    # Fecha final del periodo que queremos consultar.
    #
    # Ejemplo:
    #
    # fecha_inicio = "2026-08-17"
    # fecha_fin = "2026-08-23"
    #
    # significa que queremos consultar toda esa semana.
    fecha_fin: Optional[str] = None


    # --------------------------------------------------------
    # FILTRO POR TÍTULO
    # --------------------------------------------------------
    #
    # Este campo permite hacer consultas más específicas.
    #
    # Por ejemplo, si el usuario pregunta:
    #
    # "¿En qué aula tengo Investigación de Operaciones?"
    #
    # podemos guardar:
    #
    # filtro_titulo = "Investigación de Operaciones"
    #
    # De esta manera, el calendario puede buscar solamente
    # eventos relacionados con ese título.
    #
    # Es opcional porque la mayoría de consultas no necesitan
    # ningún filtro.
    filtro_titulo: Optional[str] = None


    # --------------------------------------------------------
    # INFORMACIÓN FALTANTE
    # --------------------------------------------------------
    #
    # Esta lista contiene los datos que todavía necesita el bot
    # para poder completar una solicitud.
    #
    # Ejemplo:
    #
    # El usuario dice:
    #
    # "Agenda una reunión"
    #
    # El bot podría detectar que falta la fecha:
    #
    # faltantes = ["fecha"]
    #
    # Otro ejemplo:
    #
    # faltantes = ["titulo", "fecha"]
    #
    # significa que todavía faltan ambas cosas.
    #
    # Al igual que recordatorios_dias, usamos
    # default_factory=list para que el valor inicial sea:
    #
    # []
    #
    # En palabras sencillas:
    #
    # "Si no falta nada, la lista simplemente está vacía".
    faltantes: list[str] = Field(default_factory=list)