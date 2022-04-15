import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

# direccion base del scraper
# a esta dirección se le aplicaran diferentes filtros y formatos segun las opciones del usuario
baseurl = "https://www.yelp.es/"

# declaramos los headers para la petición
headers = {
    'User-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'
}
# funcion aux 2: esta funcion filtra la página yelp.com por localidad para obtener la url
def filtrado(base_url):
    lugar_interes = input("Introduce el lugar de interes (Ej: bares, restaurantes, peluquerias...): ")
    localidad = input("Introduce la localidad: ")
    lugar_interes = lugar_interes.replace(" ", "+")
    localidad = localidad.replace(" ", "+")
    if lugar_interes and localidad:
        url_filtrada = base_url + "search?find_desc=" + lugar_interes + "&find_loc=" + localidad + "&ns=1"
    return url_filtrada

# funcion 1: esta funcion obtiene las urls privadas de cada item, además se realiza la paginacion
def obtener_url_privadas(url):
    hrefs = []
    puntero = True
    actual = url
    i = 1
    while (puntero):
        soup = BeautifulSoup(requests.get(actual, headers=headers).text, 'html.parser')
        lista_lugares = soup.find_all("span", class_="css-1egxyvc")
        for lugar in lista_lugares:
            href = lugar.find('a')['href']
            href_completa = baseurl + href
            hrefs.append(href_completa)
        if (soup.find('svg', class_='icon_svg')):
            actual = url + "&start=" + str(i) + "0"
            i = i + 1 
        else:
            puntero = False
    print(i)
    print(len(hrefs))
    print(hrefs)
    return hrefs

# funcion 2: esta funcion obtiene el data de interes de cada item de la página yelp.com tras haber obtenido la url de dicho item privada
def scrapear_lugar(url_privada):
    soup = BeautifulSoup(requests.get(url_privada, headers=headers).text, 'html.parser')
    try:
      title = soup.find('h1', class_="css-12dgwvn").text
    except: 
      title = "No titulo"
    try:
        datos_ubicacion = []
        [datos_ubicacion.append(data_ubi.text) for data_ubi in soup.find_all(class_="raw__09f24__T4Ezm")]
    except:
        datos_ubicacion = "No datos ubicacion"
    try:
      amenities = [my_tag.text for my_tag in soup.find_all(class_="css-1p9ibgf")]
      phone = amenities[-2]
      if re.match(r'\d{3}\s\d{3}\s\d{3}', phone):
        phone = phone
      else:
        phone = "No telefono"
    except:
      phone = "No telefono"
    try:
      tipo_establecimiento = [my_tag.text for my_tag in soup.find_all(class_="css-1fdy0l5")]
      tipo_establecimiento = tipo_establecimiento[1:-1]
    except:
      tipo_establecimiento = "No tipo establecimiento"
    try:
      puntuacion_local = soup.find('div', class_='i-stars__09f24__M1AR7')
      puntuacion_final = str(puntuacion_local['aria-label'])
      puntuacion_resultante = re.sub(r'Puntuación de ','', puntuacion_final)
      puntuacion_resultante = re.sub(r' estrellas','', puntuacion_resultante)
    except:
      puntuacion_resultante = "No tiene"
    datos_lugar = {
      'titulo': title,
      'ubicacion': datos_ubicacion,
      'tipo de establecimiento': tipo_establecimiento,
      'telefono': phone,
      'puntuacion': puntuacion_resultante
    }
    return datos_lugar

# esta funcion obtiene una lista con los datos de todos los comentarios de la página yelp.com tras haber obtenido la url de dicho lugar de interes
# unifica todo lo anterior en una sola función  
def scraper_yelp(url):
    url_filtrada = filtrado(url)
    response = requests.get(url_filtrada)
    if response.status_code != 200:
        print("Error fetching page")
        exit()
    else:
        print("Pagina encontrada")
        lista_urls_privadas = obtener_url_privadas(url_filtrada)
        lista_datos = []
        for href in lista_urls_privadas:
            datos = scrapear_lugar(href)
            lista_datos.append(datos)
            #print(datos)
        #print(lista_urls_privadas)
        #print(lista_datos)
        print("Inmuebles obtenidos")
    # output: lista de diccionarios por cada noticia: [{datos noticia 1},{datos noticia 2}]
    return lista_datos

#print(filtrado(baseurl))
obtener_url_privadas(filtrado(baseurl))
#scraper_yelp(baseurl)