# Teste Técnico - Pipeline de Dados ANS

Este projeto consiste em um pipeline de dados automatizado desenvolvido em Python para extração (Web Scraping), validação, enriquecimento e agregação de dados financeiros das operadoras de saúde, utilizando as bases públicas da ANS.

---

## 🛠️ Decisões e Trade-offs Técnicos

Abaixo estão as justificativas para as estratégias adotadas, conforme exigido no edital:

---

1. **Automação e Web Scraping**

**Estratégia:** Utilizei as bibliotecas `BeautifulSoup` e `requests` para localizar dinamicamente os links dos arquivos ZIP no portal da ANS.

**Justificativa:** Isso garante que o pipeline seja resiliente a mudanças nos nomes dos arquivos ou diretórios no servidor, desde que a estrutura do HTML permaneça consistente. Para garantir a segurança das requisições, implementei validações de URL utilizando o Pydantic (UrlSchema).

---

2. **Validação de Dados e Estratégia de "Quarentena" (Item 2.1)**

**Estratégia:** Implementei uma lógica de Marcação de Status e Segregação.

**Justificativa:** Cada registro passa por uma bateria de testes (Regex para CNPJ e valores numéricos, verificação de campos vazios e tipos de dados).

**Tratamento de Inconsistências:** 

**Valores Negativos:** Em vez de descartar, converti para positivo (multiplicando por -1), assumindo um possível erro de sinal na fonte, mas mantendo a integridade do valor.

**CNPJ/Razão Social:** Registros que falham em campos obrigatórios são movidos para o arquivo `consolidacao_despesas_invalidas.csv`. Isso evita a poluição do relatório final sem perder dados que podem ser auditados posteriormente.

---

3. **Enriquecimento e Join de Dados (Item 2.2)**

**Performance:** Na primeira etapa de filtragem **(Busca de Eventos/Sinistros)**, utilizei Mapeamento via Dicionário para associar o Registro ANS ao CNPJ e Nome, o que é computacionalmente mais rápido que um Merge em larga escala.

**Join Cadastral:** Para o join final (item 2.2), utilizei o método merge **(how='left')**. Optei por este método para identificar operadoras que possuem movimentação financeira, mas não constam no cadastro ativo, movendo-as para a quarentena com a justificativa técnica correspondente.

**Tratamento de Duplicatas:** No cadastro de operadoras, realizei a ordenação por **Data_Registro_ANS** e apliquei **drop_duplicates**, garantindo que apenas a informação cadastral mais recente fosse utilizada.

---

4. **Agregação e Performance de Memória (Item 2.3)**

**Estratégia de Chunking:** Todos os processamentos de leitura de CSV utilizam o parâmetro **chunksize**.

**Justificativa:** Esta é uma decisão crítica para lidar com o volume de dados da ANS. O processamento em lotes protege a memória RAM contra estouros (Buffer Overflow), permitindo que o script rode de forma estável em máquinas com hardware limitado.

**Métricas de Valor:** Além do total de despesas, implementei os cálculos de **Média Trimestral** e **Desvio Padrão**, tratando valores nulos com **fillna(0)** para garantir a precisão estatística do CSV final.

---

## 🚀 Como Executar o Projeto

Instale as dependências:

```bash
pip install pandas requests beautifulsoup4 pydantic
```

Execute o script principal `main.py` para iniciar o pipeline automático.

Os resultados finais serão gerados na pasta `dadosvalidados/`.