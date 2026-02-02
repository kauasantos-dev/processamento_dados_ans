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

def processar_e_consolidar(lista_arquivos_tri, caminho_cadastro, caminho_final):
    df_cad = pd.read_csv(caminho_cadastro, sep=';', encoding='utf-8', usecols=['REGISTRO_OPERADORA', 'CNPJ', 'Razao_Social'])
    df_cad['REGISTRO_OPERADORA'] = df_cad['REGISTRO_OPERADORA'].astype(str)
    
    mapa_cnpj = df_cad.set_index('REGISTRO_OPERADORA')['CNPJ'].to_dict()
    mapa_nome = df_cad.set_index('REGISTRO_OPERADORA')['Razao_Social'].to_dict()

    for info in lista_arquivos_tri:
        for chunk in pd.read_csv(info['path'], delimiter=';', decimal=',', chunksize=50000, encoding='utf-8'):
            
            filtro = chunk['DESCRICAO'].str.contains(r'\b(?:EVENTOS?|SINISTROS?)\b', case=False, na=False, regex=True)
            chunk = chunk.loc[filtro].copy()

            if not chunk.empty:
                chunk['REG_ANS'] = chunk['REG_ANS'].astype(str)
                chunk['CNPJ'] = chunk['REG_ANS'].map(mapa_cnpj)
                chunk['RazaoSocial'] = chunk['REG_ANS'].map(mapa_nome)
                chunk['Trimestre'] = info['tri']
                chunk['Ano'] = info['ano']
                
                chunk = chunk.rename(columns={'VL_SALDO_FINAL': 'ValorDespesa'})

                colunas_finais = ['CNPJ', 'RazaoSocial', 'Trimestre', 'Ano', 'ValorDespesa']
                chunk = chunk[colunas_finais]

                modo = 'w' if not os.path.exists(caminho_final) else 'a'
                header = not os.path.exists(caminho_final)
                chunk.to_csv(caminho_final, mode=modo, index=False, header=header, sep=';', encoding='utf-8')