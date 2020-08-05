import tkinter as tk
import json
import requests
import geocoder
import tkinter.scrolledtext as tkscrolled
import cv2
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os
import datetime
import numpy as np
from geopy.geocoders import Nominatim
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from PIL import Image

PRONOSTICO1D = "https://ws.smn.gob.ar/map_items/forecast/1"
PRONOSTICO2D = "https://ws.smn.gob.ar/map_items/forecast/2"
PRONOSTICO3D = "https://ws.smn.gob.ar/map_items/forecast/3"
ALERTAS_URL = "https://ws.smn.gob.ar/alerts/type/AL"
EXTENSIONES_IMG = (
    ("PNG files", "*.png"),
)
EXTENSIONES_CSV = (
    ("CSV files", "*.csv"),
)
UBICACIONES_POR_DEFECTO = [
    ["SANTA FE - PARANA", 426, 565, 42, 180],
    ["CORDOBA", 319, 422, 54, 187],
    ["SAN LUIS", 259, 318, 54, 126],
    ["MENDOZA", 158, 253, 158, 296],
    ["NEUQUEN", 134, 224, 356, 456],
    ["SANTA ROSA", 230, 387, 298, 358],
    ["SANTA FE - MERCEDES", 445, 636, 0, 38],
    ["SANTA FE - PERGAMINO", 455, 533, 235, 280],
    ["CABA - LA PLATA - GBA", 506, 585, 235, 280],
    ["BAHIA BLANCA", 388, 446, 381, 438],
    ["VIEDMA", 362, 455, 451, 502]
]
headers = {'Content-Type':'application/json',
            'Authorization':''}

def ReemplazarAcentos(texto):
    return texto.replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")

def RecortarImagen(rutaImagen, pixInicial, pixFinal):
    '''Recorta la imagen que se trae por path
    PRE: Recibe el path de una imagen y las coordenadas para recortarla
    POST: Retorna la imagen recortada y convertida a RGB
    '''
    try:
        imagen = cv2.imread(rutaImagen)
        imagenRecortada = imagen[pixInicial[0]:pixInicial[1], pixFinal[0]:pixFinal[1]]
        return cv2.cvtColor(imagenRecortada, cv2.COLOR_BGR2RGB)
    except Exception as ex:
        return ex        

def DetectarColor(colorRgb):
    '''Detecta si el color está en el rango de los rojos o púrpuras y devuelve el pronóstico correspondiente
    PRE: Recibe un color en formato RGB
    POST: Devuelve el pronóstico o una string vacía en caso de no encontrarlo o de que el color sea nulo
    '''
    try:
        if(colorRgb!='T'):
            if(colorRgb[2]>-1 and colorRgb[2]<101 and colorRgb[1]>-1 and colorRgb[1]<101 and colorRgb[0]>149):
                return "TORMENTAS DE MUCHA LLUVIA"
            elif(colorRgb[2]>149 and colorRgb[1]>-1 and colorRgb[1]<101 and colorRgb[0]>149):
                return "TORMENTAS FUERTES CON GRANIZO"
        return ""
    except Exception as ex:
        messagebox.showerror("Error", ex)
        return ""

def RetornarLocalizacionDePixels(x, y):
    '''Devuelve la zona específicada en la constante a través de una comparación en rangos de coordenadas
    PRE: Recibe las coordenadas x y
    POST: Devuelve la zona o en caso de no encontrarla, devuelve Zona desconocida
    '''
    for region in UBICACIONES_POR_DEFECTO:
        if((x>region[1] and x<region[2]) and (y>region[3] and y<region[4])):
            return region[0]
    return "Zona desconocida" 

def TraerAlertasDeImagen(imagen):
    '''Retorna las alertas en un string formateado
    PRE: Recibe una imagen en formato array
    POST: Devuelve una string conteniendo las alertas en las distintas zonas
    '''
    try:
        if(not isinstance(imagen, Exception)):
            pronosticosTotales = []
            imgToPil = Image.fromarray(imagen).convert('RGB')
            width, height = imgToPil.size
            for x in range(width):
                for y in range(height):
                    currentColor = imgToPil.getpixel((x, y))
                    pronostico = DetectarColor(currentColor)
                    if (pronostico != ""):
                        location = RetornarLocalizacionDePixels(x, y)
                        pronosticoZona = f"{pronostico} en {RetornarLocalizacionDePixels(x, y)}"
                        if(pronosticoZona not in pronosticosTotales):
                            pronosticosTotales.append(pronosticoZona)
            return '\n'.join(pronosticosTotales)
        else:
            return imagen
    except Exception as ex:
        return ex

def CrearCsvDataFrame(archivo):
    '''Crea dataFramework con los datos del archivo csv
    PRE: Recive el path de un archivo CSV
    POST: Devuelve un dataframe con la información del archivo
    '''
    try:
        df = pd.read_csv(archivo, index_col=False)
        return df
    except Exception as ex:
        return ex

def RetornarInformacionCsv(csvDataFrame, nombreColumna, periodo):
    '''Función que retorna los valores máximos de una columna especificada en un período de tiempo expresado en años
    PRE: Recibe un dataframe, la columna por la cual va a buscar la información y el período expresado en años
    POST: Devuelve el valor máximo
    '''
    try:
        csvDataFrame['Date'] = pd.to_datetime(csvDataFrame.Date)
        pastYears = csvDataFrame.set_index('Date').last(periodo)
        return pastYears[nombreColumna].max()
    except Exception as ex:
       return ex

def RetornarLocalizacionActual():
    '''Usando la libreria geocoder, devuelve la geolocalización basada en IP (lat long).
    POST: Devuelve la latitud y longitud aproximada de la IP del usuario
    '''
    try:
        miLocalizacion = geocoder.ip('me')
        return miLocalizacion.latlng
    except Exception as ex:
        return ex

def RetornarLocalizacion(indiceLocalidad):
    '''Recibe un índice de ubicación, el cual es 3 para la provincia y 2 para la ciudad.
    Devuelve la 'ciudad' o 'provincia' donde se encuentra el usuario, respectivamente.
    Glosario de índices:
    0: Número aproximado en la calle
    1: Nombre de la calle
    2: Ciudad o barrio
    3: Provincia
    4: Comuna o barrio/zona
    5: Código postal aproximado
    6: País
    PRE: Recibe el indice de localidad
    POST: Devuelve el nombre de la provincia o ciudad (o barrio) en la que se encuentra el usuario
    '''
    try:
        latLong = RetornarLocalizacionActual()
        if(not isinstance(latLong, Exception)):
            geolocator = Nominatim(user_agent="tp2")
            location = geolocator.reverse(f"{latLong[0]}, {latLong[1]}")
            return "".join(location.address.split(',')[indiceLocalidad][1:])
        else:
            return "Error al traer la ubicación actual"
    except Exception as ex:
        return ex


def ObtenerSMNjson(url):
    '''Recibe un link url, y devuelve un archivo Json "crudo" en formato JSON String.
    PRE: Recibe una url de un archivo json
    POST: Devuelve el respectivo json
    '''
    try:
        response = requests.get(url, headers=headers)
        rawJson = json.loads(response.content.decode('utf-8'))
        return json.dumps(rawJson, sort_keys=True, indent=4, default=rawJson)
    except requests.exceptions.RequestException as ex: 
        return SystemExit(ex)


def ObtenerObjetoJSON(url):
    '''Recibe un Json string y lo devuelve como un objeto Json para que pueda ser abierto e interpretado facilmente.
    PRE: Recibe una url de un json
    POST: Devuelve el json como objeto
    '''
    try:
        info = ObtenerSMNjson(url)
        if(not isinstance(info, Exception)):
            objJson=json.loads(info)
        else:
            objJson={}        
        return objJson
    except Exception as ex:
        return ex

def ObtenerURL():
    '''Crea una lista con los jsons de los pronosticos para cada dia, para poder iterar cada dia de pronosticos en la funcion VerPronostico.
    POST: Devuelve una lista de listas con todos los pronósticos de 1 a 3 días
    '''
    listaUrl = []
    unDia = ObtenerObjetoJSON(PRONOSTICO1D)
    dosDias = ObtenerObjetoJSON(PRONOSTICO2D)
    tresDias = ObtenerObjetoJSON(PRONOSTICO3D)
    listaUrl = [unDia,dosDias,tresDias]
    return listaUrl

def MostrarInfoEnVentana(texto):
    '''Recibe una cadena, abre un cuadro de texto en una ventana e imprime la cadena dentro de dicho cuadro.
    PRE: Recibe un string con el texto
    '''
    if(texto!=""):
        txtBoxWidth, txtBoxHeight = 500, 200
        ventanaAlertas = tk.Tk()
        ventanaAlertas.geometry("550x200")
        ventanaAlertas.title("Info")
        txtBoxScroll = tkscrolled.ScrolledText(master = ventanaAlertas, width = txtBoxWidth, height = txtBoxHeight, wrap='word')
        txtBoxScroll.insert(index = 1.0, chars = texto)
        txtBoxScroll.pack()
        ventanaAlertas.mainloop()
    else:
        messagebox.showinfo("Info", "No se registraron alertas")

def TodasAlertas(ubicacion,alertasStr, mostrarTodasAlertas):
    '''Recibe una provincia
    Devuelve en pantalla las alertas que involucran la provincia.
    PRE: Recibe la provincia, una string en caso de tener que mostrar previamente el pronóstico extendido y un bool que indica si debe mostrar todas las alertas
    '''
    alertas = ObtenerObjetoJSON(ALERTAS_URL)
    contador = 1
    if(mostrarTodasAlertas):
        for p in alertas:
            alertasStr+=f"Alerta n°{contador}\nTitulo: {p['title']}\nEstado: {p['status']}\Fecha: {p['date']}\nHora: {p['hour']}\nDescripcion: {p['description']}\nZonas: \n"
            for i in (p["zones"]).values():
                alertasStr += f"{i}\n"
            alertasStr+="\n\n"
            contador += 1
    else:
        if(ubicacion==""):
            ubicacion = RetornarLocalizacion(3)
        for q in alertas:
            for i in (q["zones"]).values():
                encontrado = ubicacion in i
                if(encontrado is True):
                    alertasStr+=f"Alerta n°{contador}:\nTitulo: {q['title']}\nEstado: {q['status']}\nFecha: {q['date']}\nHora: {q['hour']}\nDescripcion: {q['description']}\Zona: {i}\nLas alertas involucran su provincia, pero pueden no involucrar su ciudad."
                    contador += 1
        if(contador == 1):
            alertasStr+="No se han encontrado alertas para su provincia.\n"
    MostrarInfoEnVentana(alertasStr)

def VerPronosticoAlertas(ubicacion):
    '''Recibe una ubicación ingresada por el usuario.
    En caso de encontrar la ciudad en la base de datos, devuelve en pantalla el pronostico extendido para esa ciudad, y llama a la funcion de verAlertas con la provincia donde se encuentra la ciudad.
    PRE: Recibe una ciudad ingresada por el usuario
    '''
    try:
        listaUrl = ObtenerURL()
        chequeo = 0
        provincia = ""
        pronosticoAlertas = ""
        if(ubicacion==""):
            ubicacion = RetornarLocalizacion(3)
        for url in listaUrl:
            for p in url:
                if(p["province"] == ubicacion or p["name"]==ubicacion):
                    chequeo += 1
                    provincia = p["province"]
                    pronosticoAlertas+=f"Día {listaUrl.index(url)+1}\nTemperatura a la mañana: {p['weather']['morning_temp']}°C - Clima a la mañana: {p['weather']['morning_desc']}\nTemperatura a la tarde: {p['weather']['afternoon_temp']}°C - Clima a la tarde: {p['weather']['afternoon_desc']}\nZona: {p['name']}\n"
        if(chequeo == 0):
            pronosticoAlertas+="La ciudad ingresada no se encuentra en la base de datos o no hay pronósticos. Intente nuevamente."
        if(provincia == ""):
            TodasAlertas(ubicacion,pronosticoAlertas, False)
        else:
            TodasAlertas(provincia, pronosticoAlertas, False)
    except Exception as ex:
        messagebox.showerror("Error", ex)

def MostrarValoresMaximos(df, nombreColumna, tipoDato, periodo):
    '''Muestra la información basado en un dataframe, nombre de columba y período en años
    PRE: Recibe un dataframe, la columna por la cual va a buscar, el tipo de dato y el período expresado en años
    '''
    periodo = f"{str(periodo)}Y"
    messagebox.showinfo(message=f"{tipoDato}: {RetornarInformacionCsv(df, nombreColumna, periodo)}")


def CrearGrafico(df, ultimosAnios, tema):
    '''
    Muestra grafico con el promedio de temperaturas maximas y minimas anuales o humedad durante el periodo de tiempo especificado por (periodo).
    PRE: Recibe un dataframe, un entero con el periodo en añis y el tema del grafico (humedad o temperatura).
    POST: Grafico con los valores correspondientes del dataframe.
    '''
    try:
        listaAnio=[]
        ultimosAnios=int(ultimosAnios)
        df['Date'] = pd.to_datetime(df['Date']).dt.date
        fechaHoy=(pd.to_datetime('today')).date()
        listaTempMax = []
        listaTempMin = []
        listaHumedad = []
        for i in range(ultimosAnios, -1, -1):
            fechaInicio=fechaHoy.replace(year=fechaHoy.year-i, month=1, day =1)
            fechaFin=fechaHoy.replace(year=fechaHoy.year-i, month=12, day=31)
            listaAnio.append(fechaInicio.year)
            if(tema=="temperatura"):
                listaTempMax.append(df.loc[((df['Date']<=fechaFin) & (df['Date']>=fechaInicio)), 'Max Temperature'].mean())
                listaTempMin.append(df.loc[((df['Date']<=fechaFin) & (df['Date']>=fechaInicio)), 'Min Temperature'].mean())
            elif(tema=="humedad"):
                listaHumedad.append(df.loc[((df['Date']<=fechaFin) & (df['Date']>=fechaInicio)), 'Relative Humidity'].mean())
        if(tema=="temperatura"):
            dfPromedioTemp=pd.DataFrame({'Temperatura Maxima':listaTempMax, 'Temperatura Minima':listaTempMin}, index=listaAnio)
            grafico=dfPromedioTemp.plot.bar(title='Promedio de temperaturas anuales')
        elif(tema=="humedad"):
            dfPromedioHum=pd.DataFrame({'Promedio humedad':listaHumedad}, index=listaAnio)
            grafico=dfPromedioHum.plot.bar(title='Promedio de humedad')
        grafico.set_xlabel("Año")
        grafico.set_ylabel("Promedio")
        plt.show()
    except Exception as ex:
        messagebox.showerror("Error", ex)

def SeleccionarArchivoCsv():
    '''Abre un open file dialog para que el usuario seleccione un archivo csv
    POST: Retorna el path del archivo csv
    '''
    csvDireccion = filedialog.askopenfilename(title="Seleccione el archivo csv", filetypes=EXTENSIONES_CSV)
    if (len(csvDireccion) == 0 or (os.getcwd() != os.path.dirname(os.path.abspath(csvDireccion))) ):
        messagebox.showerror("Error", "Debe ingresar un archivo para procesar\nDebe estar en la misma carpeta que el archivo de programa")
        return ""
    return os.path.basename(csvDireccion)

def MostrarAlertasRadar():
    '''Pide al usuario seleccionar un archivo de imagen, luego ejecuta el proceso y muestra las alertas para la imagen de radar ingresada
    '''
    imagePath = filedialog.askopenfilename(title="Seleccione la imagen a analizar", filetypes=EXTENSIONES_IMG)
    if (len(imagePath) == 0):
        messagebox.showerror("Error", "Debe ingresar un archivo para procesar.")
    else:
        messagebox.showinfo("Alertas",TraerAlertasDeImagen(RecortarImagen(imagePath,[15, 555], [21, 755])))

def MenuTormenta():
    '''Crea el menu principal de la aplicación utilizando la librería tkinter
    '''
    ventanaTormenta = tk.Tk()
    ventanaTormenta.geometry("300x340")
    ventanaTormenta.title("Tormenta")
    tk.Label(ventanaTormenta, text="Bienvenidos a Tormenta").pack()
    btn_OpcionUno = tk.Button(ventanaTormenta, text = "Listar alertas por localización", command = lambda: CrearVentanaCiudad("Ingrese provincia\n(Deje en blanco para tomar ubicación actual)", True))
    btn_OpcionUno.pack(pady = 10)    
    btn_OpcionDos = tk.Button(ventanaTormenta, text = "Listar todas las alertas", command = lambda:TodasAlertas('0',"", True))
    btn_OpcionDos.pack(pady = 10)
    btn_OpcionTres = tk.Button(ventanaTormenta, text = "Mostrar gráficos", command = CrearVentanaEstadisticas)
    btn_OpcionTres.pack(pady = 10)
    btn_OpcionCuatro = tk.Button(ventanaTormenta, text = "Pronóstico extendido y alertas", command = lambda: CrearVentanaCiudad("Ingrese ubicación\n(Deje en blanco para tomar ubicación actual)", False))
    btn_OpcionCuatro.pack(pady = 10)
    btn_OptionFive = tk.Button(ventanaTormenta, text = "Analizar imagen", command=MostrarAlertasRadar)
    btn_OptionFive.pack(pady = 10)
    tk.Label(ventanaTormenta, text = RetornarLocalizacion(2)).pack()
    tk.mainloop()

def CrearVentanaEstadisticas():
    '''Crea la ventana para mostrar los gráficos y estadísticas usando la librería tkinter
    '''
    ventanaEstadisticas = tk.Tk()
    ventanaEstadisticas.geometry("300x400")
    ventanaEstadisticas.title("Seleccione una opción")
    etiquetaArchivo = tk.Label(ventanaEstadisticas, text = "Seleccione el archivo csv")
    etiquetaArchivo.pack(pady = 10)
    entradaArchivo = tk.Entry(ventanaEstadisticas)
    entradaArchivo.pack()
    btnAbrir = tk.Button(ventanaEstadisticas, text = "Seleccionar", command = lambda:entradaArchivo.insert(0,SeleccionarArchivoCsv()))
    btnAbrir.pack()
    etiquetaPeriodo = tk.Label(ventanaEstadisticas, text = "Ingrese el período en años a graficar")
    etiquetaPeriodo.pack(pady = 10)
    entradaPeriodo = tk.Entry(ventanaEstadisticas)
    entradaPeriodo.pack()
    btn_OpcionUno = tk.Button(ventanaEstadisticas, text = "Promedio de temperaturas anuales", command = lambda:CrearGrafico(CrearCsvDataFrame(entradaArchivo.get()), entradaPeriodo.get(), 'temperatura'))
    btn_OpcionUno.pack(pady = 10)  
    btn_OpcionDos = tk.Button(ventanaEstadisticas, text = "Promedio de humedad", command = lambda:CrearGrafico(CrearCsvDataFrame(entradaArchivo.get()), entradaPeriodo.get(), 'humedad'))
    btn_OpcionDos.pack(pady = 10)  
    btn_OpcionTres = tk.Button(ventanaEstadisticas, text = "Milímetros máximos de lluvia", command= lambda : MostrarValoresMaximos(CrearCsvDataFrame(entradaArchivo.get()), 'Precipitation', 'Milímetros máximos de lluvia', entradaPeriodo.get()))
    btn_OpcionTres.pack(pady = 10)  
    btn_OpcionCuatro = tk.Button(ventanaEstadisticas, text = "Temperatura máxima", command= lambda : MostrarValoresMaximos(CrearCsvDataFrame(entradaArchivo.get()), 'Max Temperature', 'Temperatura máxima (en °C)', entradaPeriodo.get()))
    btn_OpcionCuatro.pack(pady = 10)
    tk.mainloop()

def CrearVentanaCiudad(texto, soloAlertas):
    '''Crea la ventana para que el usuario pueda ingresar la ciudad y ver el pronóstico y/o las alertas usando la librería tkinter
    PRE: Recibe un bool el cual indica si son solo alertas o es alertas y pronóstico
    '''
    ventanaCiudad = tk.Tk()
    ventanaCiudad.geometry("300x150")
    ventanaCiudad.title("Seleccione ubicación")
    etiquetaCiudad = tk.Label(ventanaCiudad, text = texto)
    etiquetaCiudad.pack(pady = 10)
    entradaCiudad = tk.Entry(ventanaCiudad)
    entradaCiudad.pack(pady = 10)
    if(soloAlertas):
        btnBuscar = tk.Button(ventanaCiudad, text = "Buscar", command = lambda:TodasAlertas(entradaCiudad.get(), "", False))
    else:
        btnBuscar = tk.Button(ventanaCiudad, text = "Buscar", command = lambda:VerPronosticoAlertas(entradaCiudad.get()))
    btnBuscar.pack()
    tk.mainloop()

def main():
    MenuTormenta()

if __name__ == "__main__":
    main()