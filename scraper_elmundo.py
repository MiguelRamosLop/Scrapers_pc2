import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

# direccion base del scraper
# a esta dirección se le aplicaran diferentes filtros y formatos segun las opciones del usuario
baseurl = "https://ariadna.elmundo.es/"

# declaramos los headers para la petición
headers = {
    'User-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36'
}
# funcion aux 2: esta funcion filtra la página elmundo.com por localidad para obtener la url
def filtrar_localidad(base_url):
    localidad = input("Ingrese localidad: ")
    localidad_adaptada = localidad.replace(" ", "+")
    if localidad_adaptada: 
        url_filtrada = base_url + "buscador/archivo.html?q=" + localidad_adaptada + "&b_avanzada="
    return url_filtrada

# funcion 1: esta funcion obtiene las urls privadas de cada item, además se realiza la paginacion
def obtener_url_privadas(url):
    #print(url)
    hrefs = []
    puntero = True
    actual = url
    i = 1
    while(puntero):
        soup = BeautifulSoup(requests.get(actual, headers=headers).text, 'html.parser')
        lista_noticias = soup.find_all('h3')
        for noticia in lista_noticias:
            href = noticia.find('a')['href']
            hrefs.append(href)
        lis = soup.find_all('li')
        for li in lis:
            if li.text == "Siguiente »":
                elemento = li
        #nxt = soup.find(lambda tag:soup.name=="li" and "Siguiente" in tag.text)
        #siguiente = soup.find_all('li', string="Siguiente")
        if ((elemento) and len(hrefs) < 50):
            actual = re.sub('&b_avanzada=','&t=1&i=' + str(i) + '1&n=10&fd=0&td=0&w=70&s=1&no_acd=1', url)
            i = i + 1
        else:
            puntero = False
    #print(len(hrefs))
    #print(i)
    #print(hrefs)
    return hrefs


# funcion 2: esta funcion obtiene los datos de cada item de la página elmundo.com tras haber obtenido la url de dicho item privada
def scrapear_noticia(url_privada):
    soupNoticia = BeautifulSoup(requests.get(url_privada, headers=headers).text, 'html.parser')
    premium = soupNoticia.find('div', {'class':'ue-c-article__premium-tag'})
    if premium is None: 
        estructuraTitulo = soupNoticia.find('h1', {'class': 'ue-c-article__headline js-headline'})
        if estructuraTitulo is not None:  
            titulo = estructuraTitulo.text
        else: 
            titulo = "Noticia sin titulo"
        estructuraEntradilla = soupNoticia.find('p', {'class':'ue-c-article__standfirst'})
        if estructuraEntradilla is not None: 
            entradilla = estructuraEntradilla.text
        else: 
            entradilla = "Noticia sin entradilla"
        estructuraTexto = soupNoticia.find('div', {'class': 'ue-l-article__body ue-c-article__body'})
        if estructuraTexto is not None: 
            # Cogemos los p de la estructura de texto que conformaran todo el texto que necesitamos
            childrenTexto = estructuraTexto.findChildren("p" , recursive=False)
            texto=""
            for childTexto in childrenTexto:
                texto = texto + childTexto.text
                texto = re.sub('#',' ', texto)
        else: 
            texto = "Noticia premium, sin texto"
        datos_noticia = {
            'titulo': titulo, 
            'entradilla': entradilla, 
            'texto': texto
        }
        return datos_noticia
    else:
        return 

# esta funcion obtiene una lista con los datos de todas las noticias de la página elmundo.com tras haber obtenido la url de dicho inmueble
# unifica todo lo anterior en una sola función  
def scraper_elmundo(url):
    url_filtrada = filtrar_localidad(url)
    response = requests.get(url_filtrada)
    if response.status_code != 200:
        print("Error fetching page")
        exit()
    else:
        print("Pagina encontrada")
        lista_urls_privadas = obtener_url_privadas(url_filtrada)
        lista_datos = []
        for href in lista_urls_privadas:
            datos = scrapear_noticia(href)
            lista_datos.append(datos)
            #print(datos)
        #print(lista_urls_privadas)
        #print(lista_datos)
        print("Inmuebles obtenidos")
   # output: lista de diccionarios por cada noticia: [{datos noticia 1},{datos noticia 2}]
    return lista_datos

#print(filtrar_localidad(baseurl))
#obtener_url_privadas(baseurl)
scraper_elmundo(baseurl)