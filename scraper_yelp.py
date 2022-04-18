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
    #print(url)
    hrefs = []
    puntero = True
    actual = url
    i = 1
    while (puntero):
        soup = BeautifulSoup(requests.get(actual, headers=headers).text, 'html.parser')
        lista_lugares = soup.find_all("div", class_="container__09f24__mpR8_ hoverable__09f24__wQ_on margin-t3__09f24__riq4X margin-b3__09f24__l9v5d padding-t3__09f24__TMrIW padding-r3__09f24__eaF7p padding-b3__09f24__S8R2d padding-l3__09f24__IOjKY border--top__09f24__exYYb border--right__09f24__X7Tln border--bottom__09f24___mg5X border--left__09f24__DMOkM border-color--default__09f24__NPAKY")
        for lugar in lista_lugares:
            href = lugar.find('a')['href']
            href_completa = baseurl + href
            if (lugar.find('div', class_="i-stars__09f24__M1AR7")):
              hrefs.append(href_completa)
        if (soup.find('span', class_="icon--24-chevron-right-v2 navigation-button-icon__09f24__Bmrde css-1kq79li") and i < 2):
          # la condicion i < 2 esta hecha para que no haga tantas iteracciones. (En algunos casos la baseurl guarda hasta 24 paginas de resultados por lo que con esta condicion limitamos los outputs)
            actual = url + "&start=" + str(i) + "0"
            i = i + 1 
        else:
            puntero = False
    #print(i)
    #print(len(hrefs))
    #print(hrefs)
    return hrefs

# funcion aux 1: esta funcion hace un scraper y paginacion de los comentarios de la url privada en concreto
def scrapear_comentarios(url_privada):
  lista_comentarios = []
  actual = url_privada
  puntero = True
  i = 1
  while (puntero): 
    soup = BeautifulSoup(requests.get(actual).text, 'html.parser')
    if (soup.find('li', class_="margin-b5__09f24__pTvws border-color--default__09f24__NPAKY")):
      comentarios = soup.find_all('div', class_="review__09f24__oHr9V border-color--default__09f24__NPAKY")
      for comentario in comentarios:
        usuario = comentario.find('span', class_="fs-block css-ux5mu6").text
        texto_comentario = comentario.find('p', class_="comment__09f24__gu0rG css-qgunke").text
        fecha = comentario.find('span', class_="css-chan6m").text
        comentario = {
          'usuario': usuario, 
          'texto': texto_comentario, 
          'fecha': fecha
        }
        lista_comentarios.append(comentario)
      # realizamos la paginacion (es la misma que para las url privadas) usamos el icono (>) y si vemos que existe seguimos scrapeando. Cuando no exista se rompera la condicion del while
      if (soup.find('span', class_="icon--24-chevron-right-v2 navigation-button-icon__09f24__Bmrde css-1kq79li")):
        actual = url_privada + "&start=" + str(i) + "0"
        i = i + 1 
      else:
        puntero = False
  return lista_comentarios

# funcion 2: esta funcion obtiene el data de interes de cada item de la página yelp.com tras haber obtenido la url de dicho item privada
def scrapear_lugar(url_privada):
    soup = BeautifulSoup(requests.get(url_privada, headers=headers).text, 'html.parser')
    # scrapeamos el titulo del lugar
    try:
      title = soup.find('h1', class_="css-12dgwvn").text
    except: 
      title = "No titulo"
     # scrapeamos la ubicacion del lugar
    try:
        datos_ubicacion = []
        [datos_ubicacion.append(data_ubi.text) for data_ubi in soup.find_all(class_="raw__09f24__T4Ezm")]
    except:
        datos_ubicacion = "No datos ubicacion"
     # scrapeamos el telefono de contacto del lugar 
    try:
      amenities = [my_tag.text for my_tag in soup.find_all(class_="css-1p9ibgf")]
      phone = amenities[-2]
      if re.match(r'\d{3}\s\d{3}\s\d{3}', phone):
        phone = phone
      else:
        phone = "No telefono"
    except:
      phone = "No telefono"
     # scrapeamos el tipo de establecimiento del lugar
    try:
      tipo_establecimiento = [my_tag.text for my_tag in soup.find_all(class_="css-1fdy0l5")]
      tipo_establecimiento = tipo_establecimiento[1:-1]
    except:
      tipo_establecimiento = "No tipo establecimiento"
     # scrapeamos la calificacion del lugar
    try:
      puntuacion_local = soup.find('div', class_='i-stars__09f24__M1AR7')
      puntuacion_final = str(puntuacion_local['aria-label'])
      puntuacion_resultante = re.sub(r'Puntuación de ','', puntuacion_final)
      puntuacion_resultante = re.sub(r' estrellas','', puntuacion_resultante)
    except:
      puntuacion_resultante = "No tiene"
    # scrapeamos la direccion del lugar, en coordenadas
    try:
      coordenadas = []
      regex = r"center=(-?\d+\.\d+)%2C(-?\d+\.\d+)"
      maps = soup.find('div', class_="container__09f24__fZQnf border-color--default__09f24__NPAKY overflow--hidden__09f24___ayzG")
      srcset = maps.find('img')['srcset']
      coordenadas = re.findall(regex, srcset)
      lat_lon = coordenadas[-1]
    except: 
      lat_lon = "No lat_lon"
     # scrapeamos los comentarios del lugar
    try:
      lista_comentarios = scrapear_comentarios(url_privada)
    except:
      lista_comentarios = "No comentarios"
    
    datos_lugar = {
      'titulo': title,
      'ubicacion': datos_ubicacion,
      'tipo de establecimiento': tipo_establecimiento,
      'telefono': phone,
      'puntuacion': puntuacion_resultante,
      'coordenadas': lat_lon,
      'comentarios': lista_comentarios
    }
    print("scraper de " + url_privada + " realizado")
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
        print("Referencias obtenidas")
    # output: lista de diccionarios por cada noticia: [{datos noticia 1},{datos noticia 2}]
    return lista_datos
  
#print(filtrado(baseurl))
#obtener_url_privadas(filtrado(baseurl))
print(scraper_yelp(baseurl))
#print(scrapear_comentarios("https://www.yelp.es/biz/amagi-irish-tavern-las-rozas-de-madrid?osq=bar"))