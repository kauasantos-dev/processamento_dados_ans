import capturar_urls, processar_dados, validacoes, sys

if __name__ == '__main__':
    arquivos_zip = capturar_urls.encontrar_url_diretorio(
        link="https://dadosabertos.ans.gov.br/FTP/PDA/demonstracoes_contabeis/",
        url_diretorio_especifico="2025/"
    )

    if not arquivos_zip:
        print("ERRO: URL inválida.")
        sys.exit(0)
    
    zips_encontrados = capturar_urls.url_arquivo_zip(arquivos_zip)
    if not zips_encontrados:
        print("ERRO: Nenhum arquivo ZIP encontrado nessa URL.")
        sys.exit(0)
    else:
        print("Arquivos ZIPS encontrados!\n")
        for zip in zips_encontrados:
            arquivo_extraido = processar_dados.extrair_arquivo_zip(zip)
            if not arquivo_extraido:
                print("Erro ao extrair arquivo zip.")
                sys.exit(0)
        print("Arquivos ZIPS extraídos com sucesso!\n")

        trimestres_salvos = [
            'trimestres2025/1T2025.csv',
            'trimestres2025/2T2025.csv',
            'trimestres2025/3T2025.csv'
        ]

        trimestres_com_despesa_eventos_sinistros = []
        for trimestre in trimestres_salvos:
            possui_despesa_especifica = processar_dados.verificar_dado_especifico(trimestre, 'Despesas com eventos/sinistros')
            if possui_despesa_especifica:
                trimestres_com_despesa_eventos_sinistros.append(trimestre)
        
        if not trimestres_com_despesa_eventos_sinistros:
            print("Não há trimestres com despesas de eventos/sinistros declaradas.")
        else:
            arquivos_para_processar = []
            for trimestre in trimestres_com_despesa_eventos_sinistros:
                if trimestre == 'trimestres2025/1T2025.csv':
                    arquivos_para_processar.append(
                        {'path': 'trimestres2025/1T2025.csv', 'tri': 1, 'ano': 2025}
                    )

                elif trimestre == 'trimestres2025/2T2025.csv':
                    arquivos_para_processar.append(
                        {'path': 'trimestres2025/2T2025.csv', 'tri': 2, 'ano': 2025}
                    )

                elif trimestre == 'trimestres2025/3T2025.csv':
                    arquivos_para_processar.append(
                        {'path': 'trimestres2025/3T2025.csv', 'tri': 3, 'ano': 2025}
                    )
                    
            processar_dados.processar_e_consolidar(arquivos_para_processar, caminho_cadastro='relatorios/Relatorio_cadop.csv')

            print("Trimestres consolidados com sucesso!")

            validacoes.validar_e_marcar_dados(
                caminho_arquivo='consolidacao/consolidacao_trimestres.csv',
                diretorio_dados_validados='dadosvalidados'
            )
            print("A consolidação foi validada.\n")

            processar_dados.merge_dados_cadastrais(
                relatorio_cadop='relatorios/Relatorio_cadop.csv',
                consolidacao_despesas_validas='dadosvalidados/consolidacao_despesas_validas.csv',
                consolidacao_despesas_invalidas='dadosvalidados/consolidacao_despesas_invalidas.csv',
                caminho_arquivo_final='dadosvalidados/consolidacao_final.csv'
            )
            print("Join executado com sucesso!\n")

            processar_dados.agregar_despesas(
                consolidacao_final='dadosvalidados/consolidacao_final.csv'
            )
            print("Valor de despesa agregada com sucesso!")


    

