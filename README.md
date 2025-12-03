# 📊 Price Optimization AI: Sistema de Apoio à Decisão

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![Status](https://img.shields.io/badge/Status-Finalizado-success)

> Um sistema Full Stack para otimização de preços de venda utilizando **Cálculo Diferencial** 

---

## 📖 Sobre o Projeto
Este projeto foi desenvolvido como requisito avaliativo da disciplina de **Cálculo 1** do curso de Ciência da Computação. 

O objetivo é aplicar conceitos matemáticos (derivadas e otimização) em um problema real de engenharia de software e análise de dados. O sistema simula o ambiente de um e-commerce, modela o comportamento da demanda e recomenda o preço exato que maximiza o lucro da empresa.

### 👤 A Persona (Cliente)
* **Nome:** Ana, Gerente de Marketing.
* **O Problema:** Ana precisa definir o preço de um produto para a Black Friday. Se cobrar muito barato, a margem de lucro some. Se cobrar muito caro, as vendas despencam.
* **A Solução:** Um dashboard interativo que calcula matematicamente o ponto ótimo de equilíbrio.

---

## 🧮 Modelagem Matemática
A "mágica" por trás do sistema utiliza o **Teorema de Fermat para Pontos Estacionários**.

1.  **Função Demanda ($q$):** Estimada via Regressão Linear (`scikit-learn`) sobre dados históricos.
    $$q(p) = \alpha p + \beta$$
2.  **Função Objetivo (Lucro):**
    $$L(p) = R(p) - C(q)$$
    Onde $R$ é a receita e $C$ é o custo total.
3.  **Otimização:**
    Para encontrar o lucro máximo, calculamos a primeira derivada e igualamos a zero:
    $$\frac{dL}{dp} = 0 \implies \text{Ponto Crítico}$$
4.  **Validação:**
    O sistema verifica automaticamente a segunda derivada ($L''(p)$) para garantir que o ponto encontrado é um **Máximo Global** (concavidade voltada para baixo).

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python 3.11+
* **Frontend/Dashboard:** Streamlit
* **Cálculo Simbólico:** SymPy (para derivadas exatas)
* **Machine Learning:** Scikit-Learn (Regressão Linear)
* **Visualização:** Plotly (Gráficos interativos)
* **Manipulação de Dados:** Pandas & NumPy

---

## 🚀 Como Executar o Projeto

Siga os passos abaixo para rodar a aplicação na sua máquina local.

### Pré-requisitos
Certifique-se de ter o [Python](https://www.python.org/) instalado.

### Passo a Passo

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU_USUARIO/NOME_DO_REPO.git](https://github.com/SEU_USUARIO/NOME_DO_REPO.git)
    cd NOME_DO_REPO
    ```

2.  **Instale as dependências:**
    Recomenda-se o uso de um ambiente virtual, mas para instalação direta:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Execute o sistema:**
    ```bash
    streamlit run app/main.py
    ```
    *Nota: Se você tiver múltiplas versões do Python, use `py -3.11 -m streamlit run app/main.py`.*

O navegador abrirá automaticamente no endereço: `http://localhost:8501`.

---

## 📂 Estrutura de Arquivos

```text
/
├── app/
│   └── main.py          # Código fonte principal (Lógica + Interface)
├── data/                # (Opcional) Pasta para salvar CSVs gerados
├── requirements.txt     # Lista de bibliotecas necessárias
├── README.md            # Documentação do projeto
└── .gitignore           # Arquivos ignorados pelo Git
