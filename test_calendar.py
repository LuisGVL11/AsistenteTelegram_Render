import requests

url = "https://script.google.com/macros/s/AKfycbzeS1ebh4VfHvziQDpJzGVQt5ozyJV27H-Huaq-o8HLATLsw5nHx91dW2UfYoARTrKLPA/exec"

datos = {
    "titulo": "Prueba desde Python",
    "fecha": "2026-08-07",
    "hora": "10:00"
}


respuesta = requests.post(
    url,
    json=datos
)


print(respuesta.status_code)
print(respuesta.text)