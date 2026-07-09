# Auditoria de Modelos de Classificação para Chamados 1746

Este repositório contém a avaliação de modelos de classificação aplicados aos chamados da Central 1746.

A Central 1746 recebe milhares de chamados de cidadãos todos os dias. Para agilizar o encaminhamento, o time de IA da Casa Civil desenvolveu um classificador automático que lê o texto do chamado e prevê a categoria do serviço: o **Modelo A**, hoje em produção. Recentemente, uma nova versão foi desenvolvida: o **Modelo B**. O objetivo deste projeto é avaliar, com base em evidências estatísticas e operacionais, se vale a pena substituir o Modelo A pelo Modelo B.

Os dados utilizados são sintéticos e simulam o comportamento estatístico de um sistema real de classificação. Nenhum dado real de cidadão foi utilizado.

---

## Estrutura do Repositório

```text

├── dados/
│   ├── chamados_com_predicoes.csv
│   └── censo2022.csv
├── notebooks/
│   ├── 01_analise_exploratoria.ipynb
│   ├── 02_auditoria_modelo_a.ipynb
│   ├── 03_comparacao_e_recomendacao.ipynb
│   └── functions.py
├── results/
│   ├── figures/
│   └── tables/
├── requirements.txt
└── README.md
```

---

## Dados

Arquivo: **`dados/chamados_com_predicoes.csv`** (5.000 chamados rotulados)

| Coluna | Descrição |
|---|---|
| `id_chamado` | Identificador único |
| `data_abertura` | Data de abertura do chamado |
| `bairro` | Bairro informado |
| `canal` | Canal de entrada (app, telefone ou portal) |
| `texto` | Texto do chamado escrito pelo cidadão |
| `categoria_real` | Categoria correta, atribuída por atendente humano |
| `pred_modelo_a` | Categoria prevista pelo modelo A (produção) |
| `conf_modelo_a` | Confiança declarada pelo modelo A (0 a 1) |
| `pred_modelo_b` | Categoria prevista pelo modelo B (candidato) |
| `conf_modelo_b` | Confiança declarada pelo modelo B (0 a 1) |

Arquivo: **`dados/censo2022.csv`** 

| Coluna | Descrição |
|---|---|
| `bairro` | Bairro informado |
| `pop_bairro` | População residente do bairro em 2022 |
| `domicilios` | Domicílios presentes no bairro em 2022 |

---

## Como Reproduzir o Projeto

**1. Clonar o repositório:**

```
git clone https://github.com/iaracastro desafio-cientista-dados-junior-ia-pref.git

cd desafio-cientista-dados-junior-ia-pref
```

**2. Criar e ativar um ambiente virtual.** Com venv:

```
python -m venv .venv
source .venv/bin/activate
```

No Windows:
```
python -m venv .venv
.venv\Scripts\activate
```
Ou, usando conda:
```
conda create -n desafio-1746 python=3.11
conda activate desafio-1746
```

**3. Instalar as dependências:**
```
pip install -r requirements.txt
```
**4. Executar os notebooks.** Abra o Jupyter Notebook ou Jupyter Lab:
```
jupyter lab
```
Execute os notebooks na seguinte ordem:
```
notebooks/01_analise_exploratoria.ipynb
notebooks/02_auditoria_modelo_a.ipynb
notebooks/03_comparacao_e_recomendacao.ipynb
```
Os gráficos e tabelas gerados são salvos em:
```
results/figures/
results/tables/
```

---

## Abordagem Metodológica

### 1. Análise Exploratória dos Chamados

A primeira etapa descreve o corpus de chamados e identifica padrões relevantes para o problema de classificação. Foram analisados:

- distribuição das categorias reais dos chamados;
- distribuição por canal, bairro e tempo;
- tamanho e qualidade dos textos;
- textos muito curtos ou sem tokens úteis após limpeza;
- palavras, bigramas e trigramas mais frequentes;
- termos mais característicos por categoria usando TF-IDF;
- similaridade lexical entre categorias.

>O desempenho de um classificador de texto depende diretamente da qualidade, quantidade e diferenciação do conteúdo textual disponível. Categorias com vocabulário parecido tendem a ser mais difíceis de separar, enquanto textos muito curtos podem aumentar a chance de erro.

### 2. Auditoria do Modelo A

A segunda etapa avalia o Modelo A, atualmente em produção. Foram usadas métricas adequadas para um problema multiclasse com categorias desbalanceadas:

- **Recall Macro (Acurácia Balanceada)**: desempenho médio considerando todas as categorias com o mesmo peso;
- **F1 Macro**: medida de equilíbrio entre acertos por categoria e erros de classificação, tratando todas as categorias igualmente;
- **Kappa de Cohen**: mede a concordância entre modelo e rótulo real descontando acertos esperados ao acaso;
- **Coeficiente de Matthews**: resume a associação entre categorias reais e previstas usando a matriz de confusão completa.

A incerteza das métricas foi quantificada com intervalos de confiança por bootstrap. Esse procedimento reamostra os dados várias vezes para estimar a variabilidade esperada das métricas.

Também foram investigados modos de falha do Modelo A por meio de:

- matriz de confusão;
- desempenho por categoria;
- testes qui-quadrado para avaliar se os erros são homogêneos entre subgrupos;
- análise da confiança declarada;
- curva de calibração aproximada;
- modelo auxiliar de regressão logística para identificar fatores associados ao erro.


### 3. Comparação entre Modelo A e Modelo B

A terceira etapa compara o Modelo A com o Modelo B usando os mesmos chamados. Como ambos os modelos fazem predições sobre exatamente os mesmos registros, a comparação é pareada. Por isso, foi usado o **teste de McNemar**, que é apropriado para verificar se dois classificadores têm diferença estatisticamente relevante de acertos quando avaliados sobre os mesmos exemplos.

Além da comparação global, a análise também verificou se a melhora do Modelo B se mantém por categoria, já que um modelo pode melhorar na média, mas piorar em uma categoria operacionalmente importante.

Foram avaliados:

- ganho líquido de acertos do Modelo B em relação ao Modelo A;
- comparação global de métricas;
- teste de hipótese pareado;
- intervalos de confiança para diferenças de desempenho;
- comparação das matrizes de confusão dos dois modelos;
- comparação das curvas de calibração;
- análise da confiança declarada do Modelo B;
- ganhos e perdas por categoria em acertos, recall e F1.

---

## Principais Resultados por Etapa

### Parte 1 - Análise Exploratória

- As categorias não aparecem com a mesma frequência, o que exige cuidado na avaliação dos modelos. A acurácia isolada pode favorecer categorias maiores e esconder problemas em categorias menores. **Métricas médias precisam ser interpretadas com cautela.**

- Há variação relevante na quantidade de chamados por bairro e canal, o que pode afetar a distribuição dos textos e dos tipos de solicitação.
- O tamanho dos textos varia bastante. Textos muito curtos tendem a oferecer menos contexto para o classificador, aumentando o risco de ambiguidades.
- A análise lexical mostrou termos e expressões associados a cada categoria, o que ajuda a entender quais sinais textuais podem estar guiando os modelos.
- Algumas categorias têm vocabulário parecido, o que aumenta a chance de confusões previsíveis entre elas.

### Parte 2 - Auditoria do Modelo A

- A matriz de confusão revelou padrões de erro específicos, indicando que alguns tipos de chamados são mais difíceis para o modelo.
- Os testes de homogeneidade indicaram que a taxa de erro não é necessariamente igual entre todos os grupos avaliados.
- A confiança declarada pelo Modelo A não separa bem acertos e erros: o modelo frequentemente declara alta confiança mesmo quando erra.
- A calibração aproximada indica que a confiança do modelo deve ser usada com cautela em decisões automáticas, especialmente se ela for usada para dispensar revisão humana.

### Parte 3 - Comparação (Modelo A vs Modelo B) e Recomendação

- O Modelo B acertou cerca de 474 chamados a mais.
- A melhora global foi estatisticamente relevante no desenho pareado, isto é, considerando que os dois modelos foram avaliados nos mesmos chamados.
- O Modelo B melhorou de forma expressiva a identificação de `esgoto_vazamento`.
- A maior perda observada ocorreu em `poda_arvore`, categoria em que o Modelo B passou a deixar escapar mais chamados reais.
- A comparação por categoria mostrou que a troca é positiva na média, mas exige mitigação específica para evitar piora operacional em `poda_arvore`.

---

## Sumário Executivo

Na avaliação com os 5.000 chamados disponíveis, o Modelo B teve resultado superior ao modelo atualmente em produção. Ele classificou corretamente cerca de 474 chamados a mais do que o Modelo A, o que representa um ganho prático relevante para o encaminhamento automático dos serviços. 

A melhora não ficou restrita a um único indicador técnico: o Modelo B apresentou desempenho mais equilibrado entre diferentes tipos de chamados e corrigiu uma falha importante na categoria esgoto e vazamento, que passou a ser identificada com muito mais qualidade.

O principal risco da troca está na categoria poda de árvore. Nela, o Modelo B piorou a capacidade de identificar chamados que realmente pertencem a esse serviço. Isso significa que parte dos pedidos de poda pode ser encaminhada para o setor errado, gerando atraso, retrabalho ou necessidade de correção manual.

Por isso, a substituição é recomendada, mas deve ser acompanhada de medidas de controle. A implantação deve incluir monitoramento diário do desempenho por tipo de chamado, revisão humana temporária para solicitações com indícios de poda de árvore, acompanhamento da confiança declarada pelo modelo e um plano de retorno ao Modelo A caso a perda nessa categoria se confirme em produção.

**O veredito final é:** trocar para o Modelo B, desde que a implantação seja gradual, monitorada e com mitigação explícita para a categoria poda de árvore.

