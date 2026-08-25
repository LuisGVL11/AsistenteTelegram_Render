from ai_service import interpretar_mensaje


mensaje = "Agenda entrenamiento de fútbol el sábado a las 6 de la tarde"


resultado = interpretar_mensaje(mensaje)


print(resultado)
print()
print("Acción:", resultado.accion)
print("Título:", resultado.titulo)
print("Fecha:", resultado.fecha)
print("Hora:", resultado.hora)