import streamlit as st
import pandas as pd
import numpy as np
import sympy as sp
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
import logging
from datetime import datetime
from sqlalchemy import create_engine, text

st.set_page_config(
    page_title="Price Optimization AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

logging.basicConfig(
    filename='sistema.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)

st.markdown("""
    <style>
    .main { padding-top: 2rem; }
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05); 
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def get_db_engine():

    try:
        if "connections" in st.secrets and "postgresql" in st.secrets["connections"]:
            db = st.secrets["connections"]["postgresql"]
            # Monta a URL de conexão: postgresql+psycopg2://user:pass@host:port/db
            url = f"postgresql+psycopg2://{db['username']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}"
            engine = create_engine(url)
            return engine
        else:
            logging.error("Arquivo secrets.toml não encontrado ou mal formatado.")
            return None
    except Exception as e:
        logging.error(f"Erro ao configurar conexão DB: {e}")
        return None

def salvar_simulacao(custo_u, custo_f, preco_opt, lucro_max):
    engine = get_db_engine()
    if engine:
        try:
            dados = pd.DataFrame({
                'data_hora': [datetime.now()],
                'custo_unitario': [custo_u],
                'custo_fixo': [custo_f],
                'preco_otimo': [preco_opt],
                'lucro_maximo': [lucro_max]
            })
            
            dados.to_sql('historico_simulacoes', engine, if_exists='append', index=False)
            logging.info("Simulação salva no PostgreSQL com sucesso.")
            return True
        except Exception as e:
            logging.error(f"Erro ao inserir no banco: {e}")
            return False
    return False

def ler_historico():
    engine = get_db_engine()
    if engine:
        try:
            query = "SELECT * FROM historico_simulacoes ORDER BY data_hora DESC LIMIT 50"
            df = pd.read_sql(query, engine)
            return df
        except Exception as e:
            logging.error(f"Erro ao ler do banco: {e}")
            return pd.DataFrame() # Retorna vazio se der erro
    return pd.DataFrame()

with st.sidebar:
    st.header("⚙️ Painel de Controle")
    st.markdown("**Persona:** Ana (Gerente de Marketing)")
    st.info("Sistema de Apoio à Decisão: Otimização de Lucro")
    
    st.markdown("### 💰 Custos")
    custo_unitario = st.number_input("Custo Variável (R$/unid)", value=45.0, step=1.0)
    custo_fixo = st.number_input("Custos Fixos (R$)", value=2000.0, step=100.0)
    
    st.markdown("### 🎲 Mercado")
    sensibilidade_preco = st.slider("Elasticidade da Demanda", 1.0, 5.0, 2.5)
    ruido_dados = st.slider("Incerteza (Ruído)", 0, 100, 20)
    
    st.divider()
    st.caption("Backend: Python + PostgreSQL")


np.random.seed(42)
n_pontos = 200
precos_simulados = np.random.uniform(30, 180, n_pontos)
demanda_base = 600 - (sensibilidade_preco * precos_simulados)
vendas_simuladas = demanda_base + np.random.normal(0, ruido_dados, n_pontos)
vendas_simuladas = np.maximum(vendas_simuladas, 0)
df = pd.DataFrame({'Preco': precos_simulados, 'Vendas': vendas_simuladas})

try:
    X = df[['Preco']].values
    y = df['Vendas'].values
    modelo = LinearRegression()
    modelo.fit(X, y)
    
    a_coef = modelo.coef_[0]
    b_coef = modelo.intercept_
    logging.info(f"Modelo ML treinado. a={a_coef:.2f}, b={b_coef:.2f}")

except Exception as e:
    st.error("Erro crítico no Machine Learning.")
    logging.error(f"Erro ML: {str(e)}")
    st.stop() # Para a execução

p = sp.symbols('p')
preco_otimo = 0.0
lucro_maximo = 0.0
venda_esperada = 0.0
erro_calculo = False
salvo_no_bd = False

try:
    q_p = a_coef * p + b_coef
    receita_p = p * q_p
    custo_p = custo_unitario * q_p + custo_fixo
    lucro_p = receita_p - custo_p
    
    d_lucro = sp.diff(lucro_p, p)
    d2_lucro = sp.diff(d_lucro, p)
    
    ponto_critico = sp.solve(d_lucro, p)
    
    if ponto_critico:
        preco_otimo = float(ponto_critico[0])
        
        if preco_otimo < 0:
            raise ValueError("Preço ótimo negativo (Inviável).")
            
        lucro_maximo = float(lucro_p.subs(p, preco_otimo))
        venda_esperada = float(q_p.subs(p, preco_otimo))
        
        eh_maximo = float(d2_lucro) < 0
        
        if eh_maximo:
            salvo_no_bd = salvar_simulacao(custo_unitario, custo_fixo, preco_otimo, lucro_maximo)
        else:
            st.warning("Ponto encontrado é de Mínimo.")
    else:
        erro_calculo = True
        logging.warning("Sem raízes reais.")

except Exception as e:
    erro_calculo = True
    logging.error(f"Erro matemático: {str(e)}")
    st.error(f"Erro de Cálculo: {str(e)}")

st.title("📊 Sistema de Otimização de Preços")

tab1, tab2, tab3 = st.tabs(["💡 Dashboard", "🧮 Matemática", "🗄️ Banco de Dados"])

with tab1:
    st.subheader("Recomendação Estratégica")
    
    if not erro_calculo:
        col1, col2, col3 = st.columns(3)
        col1.metric("Preço Ideal", f"R$ {preco_otimo:.2f}", delta="Ótimo Global")
        col2.metric("Lucro Máximo", f"R$ {lucro_maximo:.2f}", delta_color="normal")
        col3.metric("Demanda", f"{int(venda_esperada)} unid")
        
        x_vals = np.linspace(max(0, preco_otimo - 50), preco_otimo + 50, 100)
        lucro_lambda = sp.lambdify(p, lucro_p, "numpy")
        y_vals = lucro_lambda(x_vals)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines', name='Curva Lucro', line=dict(color='#2ecc71', width=3)))
        fig.add_trace(go.Scatter(x=[preco_otimo], y=[lucro_maximo], mode='markers', name='Ponto Ótimo', marker=dict(color='red', size=12)))
        fig.update_layout(title="Maximização de Lucro", xaxis_title="Preço (R$)", yaxis_title="Lucro (R$)", height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Não foi possível calcular o ponto ótimo.")

with tab2:
    st.header("Memorial de Cálculo")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Função Demanda (ML)")
        st.latex(f"q(p) = {a_coef:.2f}p + {b_coef:.2f}")
    with c2:
        st.markdown("#### Função Objetivo")
        st.latex(r"L(p) = " + sp.latex(sp.expand(lucro_p)))
        
    st.divider()
    st.markdown("#### Otimização (Derivadas)")
    st.latex(r"\frac{dL}{dp} = " + sp.latex(d_lucro) + f" \implies p^* = {preco_otimo:.2f}")
    st.latex(r"\frac{d^2L}{dp^2} = " + sp.latex(d2_lucro))
    if float(d2_lucro) < 0:
        st.success("✅ Segunda derivada negativa confirma Máximo Global.")

with tab3:
    st.subheader("Integração com PostgreSQL")
    
    engine = get_db_engine()
    if engine:
        st.success("🟢 Conexão com Banco de Dados: ATIVA")
        if salvo_no_bd:
            st.toast("Simulação salva no banco com sucesso!", icon="💾")
            
        st.markdown("**Registros no Banco (Últimos 50):**")
        df_historico = ler_historico()
        if not df_historico.empty:
            st.dataframe(df_historico, use_container_width=True)
        else:
            st.info("Tabela vazia ou erro na leitura.")
    else:
        st.error("🔴 Conexão com Banco de Dados: FALHOU")
        st.info("Verifique se o PostgreSQL está rodando e se o arquivo secrets.toml está correto.")
        
    st.divider()
    st.caption("Logs do Sistema (Auditoria):")
    try:
        with open("sistema.log", "r") as f:
            st.code("".join(f.readlines()[-5:]))
    except:
        st.write("Ainda sem logs.")
