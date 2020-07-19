import json

with open('Alertas.json', encoding="utf8") as f:
    data = json.load(f)
    contador = 1
    for p in data:
        print(f"Alerta n°{contador}:")
        print(f"Titulo: {p['title']}")
        print(f"Estado: {p['status']}")
        print(f"Fecha: {p['date']}")
        print(f"Hora: {p['hour']}")
        print(f"Descripcion: {p['description']}")
        print(f"Zonas:")
        for i in (p["zones"]).values():
            print(i)
        contador += 1
        