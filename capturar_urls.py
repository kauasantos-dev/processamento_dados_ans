import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pydantic import ValidationError
from validacoes import UrlSchema

def encontrar_url_diretorio(link, url_diretorio_especifico):
    try:
        UrlSchema(url=link)
    except ValidationError:
        return None

    pagina_html = requests.get(link)
    objeto_pagina_html = BeautifulSoup(pagina_html.text, 'html.parser')

    links_diretorios = objeto_pagina_html.find_all('a')

    if links_diretorios:
        for url in links_diretorios:
            href = url.get('href')
            if href == url_diretorio_especifico:
                return urljoin(link, href)
    return None

def url_arquivo_zip(link):
    try:
        UrlSchema(url=link)
    except ValidationError:
        return None
    
    arquivos_zip_encontrados = []
    pagina_html = requests.get(link)
    objeto_pagina_html = BeautifulSoup(pagina_html.text, 'html.parser')

    link_arquivos = objeto_pagina_html.find_all('a')

    if link_arquivos:
        for link_encontrado in link_arquivos:
            href = link_encontrado.get('href')
            if href and href.endswith('.zip'):
                arquivos_zip_encontrados.append(urljoin(link, href))
    return arquivos_zip_encontrados