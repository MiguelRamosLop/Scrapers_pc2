import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

# direccion base del scraper
# a esta dirección se le aplicaran diferentes filtros y formatos segun las opciones del usuario
baseurl = "https://www.20minutos.es/"

# declaramos los headers para la petición
headers = {
    'User-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'
}
# funcion aux 2: esta funcion filtra la página 20minutos.com por localidad para obtener la url
def filtrar_localidad(base_url):
    localidad = input("Ingrese localidad: ")
    localidad_adaptada = localidad.replace(" ", "+")
    if localidad_adaptada: 
        url_filtrada = base_url + "busqueda/?q=" + localidad_adaptada + "&sort_field=&category=&publishedAt%5Bfrom%5D=&publishedAt%5Buntil%5D="
    return url_filtrada

# funcion 1: esta funcion obtiene las urls privadas de cada item, además se realiza la paginacion
def obtener_url_privadas(url):
    hrefs = []
    puntero = True
    actual = url
    i = 2
    while(puntero):
        soup = BeautifulSoup(requests.get(actual, headers=headers).text, 'html.parser')
        lista_noticias = soup.find_all('article', class_='media')
        for noticia in lista_noticias:
            h1 = noticia.find('h1')
            href = h1.find('a')['href']
            hrefs.append(href)
        if (soup.find('li', class_='last') and i < 3):
            actual = re.sub('busqueda/','busqueda/' + str(i) + '/', url)
            i = i + 1
        else:
            puntero = False
    print(len(hrefs))
    #print(hrefs)
    return hrefs


# funcion 2: esta funcion obtiene los datos de cada item de la página 20minutos.com tras haber obtenido la url de dicho item privada
def scrapear_noticia(url_privada):
    soupNoticia = BeautifulSoup(requests.get(url_privada, headers=headers).text, 'html.parser')
    titulo = soupNoticia.find('h1', {'class':'article-title'}).text
    try:
        entradilla = soupNoticia.find('div', {'id':'m35-34-36'}).text
    except: 
        entradilla = 'No entradilla'
    try:
        texto = soupNoticia.find('div', {'class':'article-text'}).text
    except: 
        texto = 'No texto'
    datos_noticia = {
        'titulo': titulo,
        'entradilla': entradilla,
        'texto': texto
    }
    return datos_noticia

# esta funcion obtiene una lista con los datos de todos los inmuebles de la página yaencontre.com tras haber obtenido la url de dicho inmueble
# unifica todo lo anterior en una sola función  
def scraper_20minutos(url):
    url_filtrada = filtrar_localidad(url)
    lista_urls_privadas = obtener_url_privadas(url_filtrada)
    lista_datos = []
    for href in lista_urls_privadas:
        datos = scrapear_noticia(href)
        lista_datos.append(datos)
        #print(datos)
    print(lista_datos)
    return lista_urls_privadas

#print(filtrar_localidad(baseurl))
#obtener_url_privadas(baseurl)
scraper_20minutos(baseurl)