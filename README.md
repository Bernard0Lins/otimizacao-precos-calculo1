# 📊 Sistema de Apoio à Decisão (SAD) para Precificação
> Um sistema Full Stack para otimização de preços de venda utilizando **Cálculo Diferencial**, **Machine Learning** e **Persistência em Banco de Dados**.

## 📖 Sobre o Projeto
Este projeto foi desenvolvido como requisito avaliativo da disciplina de **Cálculo 1** do curso de Ciência da Computação. 

O objetivo é aplicar conceitos matemáticos (derivadas e otimização) em um problema real de engenharia de software e análise de dados. O sistema simula o ambiente de um e-commerce, modela o comportamento da demanda via IA e recomenda o preço exato que maximiza o lucro da empresa, salvando as decisões em um banco de dados relacional.

### 👤 A Persona (Cliente)
* **Nome:** Ana, Gerente de Marketing.
* **O Problema:** Ana precisa definir o preço de um produto para a Black Friday. Se cobrar muito barato, a margem de lucro some. Se cobrar muito caro, as vendas despencam.
* **A Solução:** Um dashboard interativo que calcula matematicamente o ponto ótimo de equilíbrio e mantém um histórico auditável das simulações.

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
* **Frontend:** Streamlit
* **Banco de Dados:** PostgreSQL (via SQLAlchemy e psycopg2)
* **Matemática Simbólica:** SymPy (Derivadas Exatas)
* **Machine Learning:** Scikit-Learn
* **Logs & Auditoria:** Python Logging

---

## 🚀 Como Executar o Projeto

Siga os passos abaixo para rodar a aplicação na sua máquina local.

Pré-requisitos

Python 3.11+ instalado.

PostgreSQL instalado e rodando.

## 1. Clonar e Instalar

Abra o terminal e execute:

# Clone o repositório
git clone [https://github.com/SEU_USUARIO/NOME_DO_REPO.git](https://github.com/SEU_USUARIO/NOME_DO_REPO.git)
cd NOME_DO_REPO

# Instale as dependências
pip install -r requirements.txt


## 2. Preparar o Banco de Dados

Abra o pgAdmin (ou terminal do Postgres).

Crie um banco de dados chamado calculo_db.

Abra a "Query Tool" desse banco e rode o código abaixo para criar a tabela:

CREATE TABLE historico_simulacoes (
    id SERIAL PRIMARY KEY,
    data_hora TIMESTAMP,
    custo_unitario FLOAT,
    custo_fixo FLOAT,
    preco_otimo FLOAT,
    lucro_maximo FLOAT
);


3. Configurar a Senha (Obrigatório)

O sistema precisa da senha do seu banco local para conectar. Por segurança, ela não fica salva no Git.

Na raiz do projeto, crie uma pasta chamada .streamlit.

Dentro dela, crie um arquivo chamado secrets.toml.

Cole o conteúdo abaixo e insira sua senha:

# Arquivo: .streamlit/secrets.toml

[connections.postgresql]
dialect = "postgresql"
username = "postgres"
password = "SUA_SENHA_DO_POSTGRES_AQUI"
host = "localhost"
port = "5432"
database = "calculo_db"


4. Rodar o Sistema

No terminal, execute:

streamlit run app/main.py


O navegador abrirá automaticamente em http://localhost:8501.
