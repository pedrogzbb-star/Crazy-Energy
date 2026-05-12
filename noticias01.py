
import requests
from bs4 import BeautifulSoup

def buscar_noticias_energia():
    # Buscamos "energía eléctrica" en Google News España
    url = "https://news.google.com/search?q=energia%20electrica%20when:1d&hl=es-419&gl=ES&ceid=ES:es"
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # En 2026 los selectores pueden variar, buscamos etiquetas de artículos
    articulos = soup.find_all('article')

    for item in articulos[:5]:  # Mostrar los primeros 5
        titulo = item.find('a', {'class': 'J7Yfub'}) # Ejemplo de clase
        if titulo:
            print(f"Título: {titulo.text}")
            print(f"Enlace: https://news.google.com{titulo['href'][1:]}\n")

buscar_noticias_energia()
