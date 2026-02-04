import os, pandas as pd
from pydantic import HttpUrl, BaseModel

class UrlSchema(BaseModel):
    url: HttpUrl

def validar_caminho(caminho, tipo='ambos'):
    if not os.path.exists(caminho):
        return False
        
    if tipo == 'arquivo':
        return os.path.isfile(caminho)
    elif tipo == 'diretorio':
        return os.path.isdir(caminho)
    
    return True

def validar_e_marcar_dados(
        caminho_arquivo, 
        diretorio_dados_validados='dadosvalidados'
    ):

    os.makedirs(diretorio_dados_validados, exist_ok=True)

    arquivo_dados_validos = os.path.join(diretorio_dados_validados, 'consolidacao_despesas_validas.csv')
    
    arquivo_dados_invalidos = os.path.join(diretorio_dados_validados, 'consolidacao_despesas_invalidas.csv')

    for df in pd.read_csv(caminho_arquivo, sep=';', chunksize=20000, encoding='utf-8'):

        df['Status_Validacao'] = 'Valido'
        df['Motivo_Erro'] = ''

        valor_invalido = ~df['ValorDespesa'].astype(str).str.match(r'^-?[0-9]+(\.[0-9]+)?$')
        df.loc[valor_invalido, 'Status_Validacao'] = 'Invalido'
        df.loc[valor_invalido, 'Motivo_Erro'] += 'Valor com Caracteres Invalidos; '

        despesas_invalidas = df['ValorDespesa'] < 0
        df.loc[despesas_invalidas, 'ValorDespesa'] *= -1

        despesa_igual_a_zero = df['ValorDespesa'] == 0
        df.loc[despesa_igual_a_zero, 'Status_Validacao'] = 'Invalido'
        df.loc[despesa_igual_a_zero, 'Motivo_Erro'] += 'Valor de despesa igual a 0; '
    
        df['CNPJ'] = df['CNPJ'].astype(str).str.replace(r'\.0$', '', regex=True)
        df['CNPJ'] = df['CNPJ'].astype(str).str.replace(r'[^0-9]', '', regex=True)

        tamanho_cnpj = df['CNPJ'].astype(str).str.len() != 14
        df.loc[tamanho_cnpj, 'Status_Validacao'] = 'Invalido'
        df.loc[tamanho_cnpj, 'Motivo_Erro'] += 'CNPJ Incompleto; '

        razao_social_vazia = df['RazaoSocial'].isna() | (df['RazaoSocial'].astype(str).str.strip() == "")
        df.loc[razao_social_vazia, 'Status_Validacao'] = 'Invalido'
        df.loc[razao_social_vazia, 'Motivo_Erro'] += 'Razao Social Vazia; '

        trimestre_invalido = ~df['Trimestre'].astype(str).str.isdigit()
        ano_invalido = ~df['Ano'].astype(str).str.isdigit()
    
        tempo_invalido = trimestre_invalido | ano_invalido

        df.loc[tempo_invalido, 'Status_Validacao'] = 'Invalido'
        df.loc[tempo_invalido, 'Motivo_Erro'] += 'Trimestre ou Ano com Caracteres Invalidos; '

        df_dados_validos = df[df['Status_Validacao'] == 'Valido']
        df_dados_invalidos = df[df['Status_Validacao']  == 'Invalido']

        primeira_escrita_dados_validos = not os.path.exists(arquivo_dados_validos)

        primeira_escrita_dados_invalidos = not os.path.exists(arquivo_dados_invalidos)

        df_dados_validos.to_csv(arquivo_dados_validos, mode='a', index=False, sep=';', encoding='utf-8', header=primeira_escrita_dados_validos)

        df_dados_invalidos.to_csv(arquivo_dados_invalidos, mode='a', index=False, sep=';', encoding='utf-8', header=primeira_escrita_dados_invalidos)