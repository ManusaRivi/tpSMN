import json

pueblos_1 = ["Tunuyan","San Rafael","Punta de Vacas","Uspallata","Mendoza","San Martín","Malargüe","San Carlos"]
pueblos_2 = ["Zapala","Chapelco","Villa la Angostura","San Martín de Los Andes"]
pueblos_3 = ["El Bolsón","San Carlos de Bariloche"]
pueblos_4 = ["San Juan"]
pueblos_5 = ["Esquel"]
pueblos_6 = ["San Rafael","Malargüe","San Carlos"]
pueblos_7 = ["San Carlos de Bolívar","Pinamar","Azul","9 de Julio","Maipú","Las Flores","Olavarría","Tandil","Coronel Pringles","Balcarce","Mar del Plata","Pigüé","Monte Hermoso","Tres Arroyos","Miramar","Bahía Blanca","Villa Gesell","Benito Juárez","Necochea"]
pueblos_8 = ["Victorica","Eduardo Castex","25 de Mayo","Santa Rosa","General Acha","General Pico","Intendente Alvear"]
pueblos_9 = ["General Alvear","Malargüe"]
pueblos_10 = ["Neuquén","Zapala","Cutral Co"]
pueblos_11 = ["Río Colorado","San Antonio Oeste","Viedma","El Bolsón","San Carlos de Bariloche","Maquinchao"]
pueblos_12 = ["Quilmes","Punta Indio","La Plata","Avellaneda","San Isidro"]

regiones = {"Zona cordillerana y precordillerana de Mendoza": pueblos_1,"Zona cordillerana de Neuquén": pueblos_2,"Zona cordillerana de Río Negro": pueblos_3,"Zona cordillerana del sur de San Juan": pueblos_4,"Zona cordillerana del norte de Chubut": pueblos_5,"Zona cordillerana del centro y sur de Mendoza": pueblos_6,"Centro y sur de la provincia de Buenos Aires": pueblos_7,"La Pampa": pueblos_8,"Sur de Mendoza": pueblos_9,"Oeste, centro y este de Neuquén": pueblos_10,"Oeste, centro y este de Río Negro": pueblos_11,"Río de la Plata exterior": pueblos_12}

ciudad = input("Ingrese su ciudad: ")
with open('Pronostico 3 dias.json', encoding="utf8") as f, open('Alertas.json', encoding="utf8") as a:
    data = json.load(f)
    for p in data:
        if(p["name"] == ciudad):
            print("Pronostico dentro de tres dias:")
            print(f"Por la mañana, el clima es: {p['weather']['morning_desc']}. La temperatura es de {p['weather']['morning_temp']}°C.")
            print(f"Por la tarde, el clima es: {p['weather']['afternoon_desc']}. La temperatura es de {p['weather']['afternoon_temp']}°C.")
    alertas = json.load(a)
    contador = 1
    for q in alertas:
        for i in (q["zones"]).values():
            encontrado = ciudad in regiones[i]
            if(encontrado is True):
                print(f"Alerta n°{contador}:")
                print(f"Titulo: {q['title']}")
                print(f"Estado: {q['status']}")
                print(f"Fecha: {q['date']}")
                print(f"Hora: {q['hour']}")
                print(f"Descripcion: {q['description']}")
                contador += 1

