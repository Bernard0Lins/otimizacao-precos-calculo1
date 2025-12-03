import streamlit as st
import pandas as pd
import numpy as np
import sympy as sp
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go
import plotly.express as px

# --- CONFIGURAÇÃO DA PÁGINA (UX Profissional) ---
st.set_page_config(
    page_title="Price Optimization AI",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CORREÇÃO DO VISUAL (CSS) ---
# Aqui removemos o fundo branco forçado para funcionar bem no Modo Escuro
st.markdown("""
    <style>
    .main { padding-top: 2rem; }
    /* Estilo dos cartões de métrica: Fundo escuro translúcido e borda sutil */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05); 
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: CONTROLE DO USUÁRIO ---
with st.sidebar:
    st.header("⚙️ Painel de Controle")
    st.markdown("**Persona:** Ana (Gerente de Marketing)")
    st.info("Ajuste os parâmetros abaixo para simular diferentes cenários de mercado.")
    
    st.markdown("### 💰 Estrutura de Custos")
    custo_unitario = st.number_input("Custo por Unidade (R$)", value=45.0, step=1.0, help="Quanto custa para comprar/produzir um item.")
    custo_fixo = st.number_input("Custos Fixos Totais (R$)", value=2000.0, step=100.0, help="Aluguel, salários, luz, etc.")
    
    st.markdown("### 🎲 Simulação de Mercado")
    sensibilidade_preco = st.slider("Sensibilidade do Cliente", 1.0, 5.0, 2.5, help="Quanto maior, mais clientes desistem quando o preço sobe.")
    ruido_dados = st.slider("Instabilidade (Ruído)", 0, 100, 20, help="Simula a 'sujeira' de dados reais.")
    
    st.divider()
    st.caption("Sistema v1.0 - Projeto Cálculo 1")

# --- LÓGICA DO SISTEMA ---

# 1. GERAÇÃO DE DADOS SINTÉTICOS
np.random.seed(42)
n_pontos = 200
precos_simulados = np.random.uniform(30, 180, n_pontos)
# Equação oculta: Demanda = Intercepto - (Coef * Preço) + Ruído
demanda_base = 600 - (sensibilidade_preco * precos_simulados)
vendas_simuladas = demanda_base + np.random.normal(0, ruido_dados, n_pontos)
vendas_simuladas = np.maximum(vendas_simuladas, 0) # Não existe venda negativa

df = pd.DataFrame({'Preco': precos_simulados, 'Vendas': vendas_simuladas})

# 2. MODELAGEM (Machine Learning - Sklearn)
X = df[['Preco']].values
y = df['Vendas'].values
modelo = LinearRegression()
modelo.fit(X, y)

a_coef = modelo.coef_[0]   # Inclinação da reta (Slope)
b_coef = modelo.intercept_ # Intercepto

# 3. CÁLCULO SIMBÓLICO (SymPy)
p = sp.symbols('p') # Variável simbólica 'preço'
q_p = a_coef * p + b_coef                 # Função Demanda
receita_p = p * q_p                       # Função Receita
custo_p = custo_unitario * q_p + custo_fixo # Função Custo
lucro_p = receita_p - custo_p             # Função Lucro Objetivo

# Derivadas
d_lucro = sp.diff(lucro_p, p)             # 1ª Derivada
d2_lucro = sp.diff(d_lucro, p)            # 2ª Derivada

# Otimização (Achar onde a derivada é zero)
ponto_critico = sp.solve(d_lucro, p)
if ponto_critico:
    preco_otimo = float(ponto_critico[0])
    lucro_maximo = float(lucro_p.subs(p, preco_otimo))
    venda_esperada = float(q_p.subs(p, preco_otimo))
else:
    preco_otimo = 0.0
    lucro_maximo = 0.0
    venda_esperada = 0.0

# --- INTERFACE PRINCIPAL ---

st.title("📊 Sistema de Otimização de Preços")
st.markdown("Este sistema utiliza **Cálculo Diferencial** e **Machine Learning** para recomendar a melhor decisão de preço.")

# Criando Abas para organizar o conteúdo
tab1, tab2, tab3 = st.tabs(["💡 Recomendação (Dashboard)", "🧮 Relatório Matemático", "📂 Dados Brutos"])

with tab1:
    # --- ABA 1: O QUE A GERENTE QUER VER ---
    st.subheader("Resultados da Análise")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Preço Ideal de Venda", f"R$ {preco_otimo:.2f}", delta="Recomendado")
    col2.metric("Lucro Máximo Estimado", f"R$ {lucro_maximo:.2f}", delta_color="normal")
    col3.metric("Vendas Esperadas", f"{int(venda_esperada)} und", delta="Volume Ótimo")
    
    st.divider()
    
    # Gráfico Principal: Curva de Lucro
    x_range = np.linspace(30, 180, 100)
    lucro_func = sp.lambdify(p, lucro_p, "numpy") # Transforma sympy em função python
    y_lucro = lucro_func(x_range)
    
    fig = go.Figure()
    
    # Linha do Lucro
    fig.add_trace(go.Scatter(x=x_range, y=y_lucro, mode='lines', name='Curva de Lucro', 
                             line=dict(color='#2ecc71', width=3)))
    
    # Ponto Ótimo
    fig.add_trace(go.Scatter(x=[preco_otimo], y=[lucro_maximo], mode='markers+text', 
                             name='Ponto Máximo', text=['  Preço Ótimo'], textposition="top right",
                             marker=dict(size=12, color='red', symbol='star')))

    fig.update_layout(title="Análise de Concavidade: Maximização de Lucro",
                      xaxis_title="Preço de Venda (R$)",
                      yaxis_title="Lucro Resultante (R$)",
                      hovermode="x unified", height=500)
    
    st.plotly_chart(fig, use_container_width=True)
    st.info("📌 **Nota Técnica:** O ponto vermelho indica o topo da parábola, onde a derivada da função lucro é igual a zero ($L'(p) = 0$).")

with tab2:
    # --- ABA 2: O QUE O PROFESSOR DE CÁLCULO QUER VER ---
    st.header("Memorial de Cálculo")
    st.markdown("Detalhamento rigoroso da modelagem matemática aplicada.")
    
    col_math1, col_math2 = st.columns(2)
    
    with col_math1:
        st.subheader("1. Modelagem da Demanda")
        st.write("A partir da Regressão Linear dos dados históricos, obtivemos:")
        st.latex(r"q(p) \approx " + f"{a_coef:.2f}p + {b_coef:.2f}")
        
        # Gráfico da Regressão
        fig_reg = px.scatter(df, x='Preco', y='Vendas', opacity=0.4, title="Regressão Linear: Preço vs Demanda")
        fig_reg.add_trace(go.Scatter(x=x_range, y=a_coef*x_range + b_coef, mode='lines', name='Modelo', line=dict(color='red')))
        st.plotly_chart(fig_reg, use_container_width=True)

    with col_math2:
        st.subheader("2. Função Objetivo e Otimização")
        st.write("Definimos a função Lucro $L(p)$ como Receita - Custo Total:")
        
        st.latex(r"L(p) = p \cdot q(p) - (C_{unit} \cdot q(p) + C_{fixo})")
        
        st.write("Substituindo $q(p)$ e simplificando (SymPy):")
        st.latex(r"L(p) = " + sp.latex(sp.expand(lucro_p)))
        
        st.markdown("---")
        st.write("**3. Critério da Primeira Derivada ($L' = 0$):**")
        st.latex(r"\frac{dL}{dp} = " + sp.latex(d_lucro))
        st.write(f"Igualando a zero, encontramos o ponto crítico: $p = {preco_otimo:.2f}$")
        
        st.write("**4. Critério da Segunda Derivada ($L'' < 0$):**")
        st.latex(r"\frac{d^2L}{dp^2} = " + sp.latex(d2_lucro))
        
        if d2_lucro < 0:
            st.success(f"Como a segunda derivada é negativa ({d2_lucro:.2f} < 0), comprovamos matematicamente que este é um ponto de **MÁXIMO** global.")
        else:
            st.error("Ponto de Mínimo detectado.")

with tab3:
    # --- ABA 3: DADOS ---
    st.subheader("Base de Dados Histórica")
    st.write("Dados utilizados para o treinamento do modelo de Machine Learning.")
    st.dataframe(df, use_container_width=True)
    
    # Download button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Baixar Dataset (.csv)", data=csv, file_name="dados_vendas.csv", mime="text/csv")