from ai_service import interpretar_mensaje


mensaje = "Agenda examen de matemáticas el 10 de agosto a las 8 de la mañana"


resultado = interpretar_mensaje(mensaje)


print(resultado)

print("Acción:", resultado.accion)
print("Título:", resultado.titulo)
print("Fecha:", resultado.fecha)
print("Hora:", resultado.hora)