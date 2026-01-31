import os
import io
import requests
import pandas as pd
from zipfile import ZipFile

def extrair_arquivo_zip(url_zip, pasta_destino='trimestres_2025'):
    os.makedirs(pasta_destino, exist_ok=True)

    try:
        arquivo_zip = requests.get(url_zip, timeout=20)
        arquivo_zip.raise_for_status()
    except requests.RequestException:
        return False
    
    with ZipFile(io.BytesIO(arquivo_zip.content)) as file:
        file.extractall(pasta_destino)

    return True

def verificar_dado_especifico(caminho_arquivo, dado_especifico):
    for chunk in pd.read_csv(caminho_arquivo, delimiter=';', chunksize=10000):
        dado_encontrado = chunk.astype(str).apply(lambda x: x.str.contains(str(dado_especifico), case=False, na=False)).any().any()
        if dado_encontrado:
            return True
    return False 