import os
import io
import requests
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