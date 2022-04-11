# import requests
# from bs4 import BeautifulSoup
# import geocoder

# url = "https://www.yelp.com/biz/naomi-madrid"

# html = requests.get(url)

# web = BeautifulSoup(html.text, 'html.parser')

# contenedor_telefono = web.find(class_='arrange__09f24__LDfbs gutter-2__09f24__CCmUo vertical-align-middle__09f24__zU9sE border-color--default__09f24__NPAKY')

# telf = contenedor_telefono.find(class_='css-1p9ibgf').text

# ubicacion = web.find(class_="raw__09f24__T4Ezm").text
# print(ubicacion)

# r = geocoder.google(ubicacion, key="AIzaSyDRAeyHmATSjGB87aUqWTUEkYMeYjtdN0c")

# print(r.address)

# lat, long = r.latlng
# print(lat)




#Glosario de imports

from bs4 import BeautifulSoup
import requests
import re
import os
from datetime import datetime
import re
import random
import geocoder

ubicacion = input()
url = 'https://www.yelp.es/search?find_desc=&find_loc=' + ubicacion + '%2C+Madrid&start='
url
lista_paginas = []
for num in range(0, 50, 10):
    lista_paginas.append(num)

lista_urls = []
for i in lista_paginas:
    url_lista = url + str(i)
    i = i + 1
    lista_urls.append(url_lista)
#Metodos sacar URL's de cada medio

def lista_urls_restaurantes(url):
    lista = [] 
    html = requests.get(url)

    web = BeautifulSoup(html.text, 'html.parser')
    noticias = web.find_all("h3", class_="css-kagwww")
    

    for url in noticias:
        url_restaurante = url.find('a').get('href')
        url_restaurante = "https://www.yelp.es/" + url_restaurante
        lista.append(url_restaurante)
    return lista
lista_locales = []
for url in lista_urls:
    lst = lista_urls_restaurantes(url)
    lista_locales.append(lst)

lista_completa = []
for local in lista_locales:
    lista_completa +=local
    

def GET_UA():
    uastrings = ["Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/8.0 Safari/600.1.25",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",\
                "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",\
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/600.1.17 (KHTML, like Gecko) Version/7.1 Safari/537.85.10",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",\
                "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",\
                "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.104 Safari/537.36"\
                ]
 
    return random.choice(uastrings)

headers = {'User-Agent': GET_UA()}

def guardar_locales(lista_urls_completa):
    lista_sitios = []
    lista_comentarios = []

    for url in lista_urls_completa:
        html = requests.get(url, headers = headers )
        web = BeautifulSoup(html.text, 'html.parser')
        
        #Nombre 
        nombre_local = web.find('h1', class_="css-12dgwvn")
        if nombre_local == None:
            nombre_local = "No tiene"
        else:
            nombre_local = nombre_local.text
    
        
        #Puntuacion
        puntuacion_local = web.find('div', class_='i-stars__09f24__M1AR7 i-stars--large-4-half__09f24__pXLBr border-color--default__09f24__NPAKY overflow--hidden__09f24___ayzG')
        try:
            puntuacion_local = web.find('div', class_='i-stars__09f24__M1AR7 i-stars--large-4-half__09f24__pXLBr border-color--default__09f24__NPAKY overflow--hidden__09f24___ayzG')
            puntuacion_final = str(puntuacion_local['aria-label'])
            puntuacion_numerica = re.search("(\d[\.,]\d|\d)", puntuacion_final)
            puntuacion_resultante = puntuacion_numerica.group(0)
            
        except:
            puntuacion_final = "No tiene"

        
        #Telefono
        contenedor_telf = web.find('div', class_='css-xp8w2v padding-t2__09f24__Y6duA padding-r2__09f24__ByXi4 padding-b2__09f24__F0z5y padding-l2__09f24__kf_t_ border--top__09f24__exYYb border--right__09f24__X7Tln border--bottom__09f24___mg5X border--left__09f24__DMOkM border-radius--regular__09f24__MLlCO background-color--white__09f24__ulvSM')
        textos = contenedor_telf.find_all('p')
        completo = ""
        for texto in textos:
            completo += texto.text
        expresion_telf = re.search(r'(\d{3}[-\s]?\d{3}[-\s]?\d{3})', completo)
        telefono = expresion_telf.group(0)
        
        #Direccion
        direccion = web.find('span', class_='raw__09f24__T4Ezm').text
        # maps = geocoder.google(direccion, key='AIzaSyAMot24WThCTr8aJCBRlvLzrUrrmqhKLlM')
        # dire = maps.address
        # lat, long = maps.latlng

        # sitio_interes = {"nombre": nombre_local, "puntuacion": puntuacion_resultante, "telefono": telefono, "direccion": dire, "latitud": lat, "longitud": long}
        # paginas = web.find_all(class_="undefined display--inline-block__09f24__fEDiJ border-color--default__09f24__NPAKY")

        # ultima = int(paginas[-1].text)

        # limite = (ultima * 10) - 10

        # for resultado in range(0,limite + 10, 10):
        url_res = url + "?start="
        h = requests.get(url_res)
        w = BeautifulSoup(h.text, 'html.parser')
        comentarios = w.find_all(class_="review__09f24__oHr9V border-color--default__09f24__NPAKY")
        for comentario in comentarios:
            usuario = comentario.find(class_="fs-block css-ux5mu6").text
            texto_comentario = comentario.find(class_="comment__09f24__gu0rG css-qgunke").text
            fecha = comentario.find(class_="css-chan6m").text
            comentario = {'usuario': usuario, 'texto': texto_comentario, 'fecha': fecha}
            lista_comentarios.append(comentario)
            sitio_interes = {"nombre": nombre_local, "puntuacion": puntuacion_resultante, "telefono": telefono, "direccion": direccion, "comentarios": lista_comentarios}
            lista_sitios.append(sitio_interes)

            print(lista_sitios)
guardar_locales(lista_completa)
