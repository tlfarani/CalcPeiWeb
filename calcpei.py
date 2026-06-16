import streamlit as st
import pandas as pd
import math

# Configuração inicial da página
st.set_page_config(page_title="CalcPEI - Mac & Nuvem", page_icon="💧", layout="wide")

st.title("Calculadora PEI (CalcPEI)")
st.caption("Dimensionamento de Capacidade Mínima de Resposta - Resolução CONAMA nº 398/2008")

# --- PASSO 1: ENTRADA DE DADOS (Substituindo os Radio Buttons do VB) ---
st.sidebar.header("1. Parâmetros de Entrada")

tipo_instalacao = st.sidebar.selectbox(
    "Tipo de Instalação / Fonte de Risco:",
    [
        "Tanques, equipamentos de processo e navios",
        "Dutos",
        "Plataformas de perfuração exploratória ou de desenvolvimento",
        "Plataformas de produção",
        "Instalações terrestres de produção",
        "Operações de carga e descarga",
        "Plataformas de armazenamento associadas a plataformas de produção"
    ]
)

# Renderização dinâmica dos campos de volume baseada na seleção (Substituindo gpxA, gpxB, etc.)
Vpc = 0.0

if tipo_instalacao == "Tanques, equipamentos de processo e navios":
    v1a = st.sidebar.number_input("Volume V1 (m³):", min_value=0.0, value=0.0, step=1.0)
    Vpc = v1a

elif tipo_instalacao == "Dutos":
    t1b = st.sidebar.number_input("Tempo T1 (h):", min_value=0.0, value=0.0)
    t2b = st.sidebar.number_input("Tempo T2 (h):", min_value=0.0, value=0.0)
    q1b = st.sidebar.number_input("Vazão Q1 (m³/h):", min_value=0.0, value=0.0)
    v1b = st.sidebar.number_input("Volume V1 (m³):", min_value=0.0, value=0.0)
    Vpc = (t1b + t2b) * q1b + v1b

elif tipo_instalacao == "Plataformas de perfuração exploratória ou de desenvolvimento":
    v1c = st.sidebar.number_input("Volume V1 (m³):", min_value=0.0, value=0.0)
    Vpc = v1c

elif tipo_instalacao == "Plataformas de produção":
    v1d = st.sidebar.number_input("Volume V1 (m³):", min_value=0.0, value=0.0)
    v2d = st.sidebar.number_input("Volume V2 (m³):", min_value=0.0, value=0.0)
    Vpc = v1d + v2d

elif tipo_instalacao == "Instalações terrestres de produção":
    v1e = st.sidebar.number_input("Volume V1 (m³):", min_value=0.0, value=0.0)
    Vpc = v1e

elif tipo_instalacao == "Operações de carga e descarga":
    t1f = st.sidebar.number_input("Tempo T1 (h):", min_value=0.0, value=0.0)
    t2f = st.sidebar.number_input("Tempo T2 (h):", min_value=0.0, value=0.0)
    q1f = st.sidebar.number_input("Vazão Q1 (m³/h):", min_value=0.0, value=0.0)
    Vpc = (t1f + t2f) * q1f

elif tipo_instalacao == "Plataformas de armazenamento associadas a plataformas de produção":
    v1g = st.sidebar.number_input("Volume V1 (m³):", min_value=0.0, value=0.0)
    Vpc = v1g

# --- PASSO 2: LOCAL E GEOMETRIA ---
st.sidebar.subheader("2. Local do Derramamento")
local = st.sidebar.radio(
    "Ambiente:",
    ["Zona Costeira, lagos, represas e outros lenticos", 
     "Rios e outros ambientes lóticos", 
     "Águas marítimas além da Zona Costeira"]
)

st.sidebar.subheader("3. Características Geométricas")
comprimento = st.sidebar.number_input("Comprimento do navio/fonte (m):", min_value=0.0, value=0.0)
largura = st.sidebar.number_input("Largura do corpo hídrico (m):", min_value=0.0, value=0.0)
velocidade = st.sidebar.number_input("Velocidade máxima da corrente (nós/m/s):", min_value=0.0, value=0.0)
linha_protecao = st.sidebar.number_input("Comprimento da linha de proteção (m):", min_value=0.0, value=0.0)

# --- PASSO 3: BOTÃO DE CÁLCULO E LOGICA MATEMÁTICA ---
if st.sidebar.button("Calcular Dimensionamento", type="primary"):
    
    # Validação simples de segurança
    if Vpc == 0:
        st.error("O Volume de Pior Caso (Vpc) não pode ser zero. Verifique os dados de entrada.")
    else:
        # 1. Cálculos de Recolhedores (Pequena e Média)
        if Vpc <= 8:
            Cdp = Vpc
        else:
            Cdp = 8.0
        CNRdp = Cdp / 24 / 0.2
        Armazdp = CNRdp * 3

        Vpcm = 0.0
        Cdm = 0.0
        if 8 < Vpc <= 80:
            Cdm = 8.0
            Vpcm = Cdm
        elif 80 < Vpc <= 160:
            Cdm = 8.0
            Vpcm = 0.1 * Vpc
        elif 160 < Vpc <= 2000:
            Cdm = 0.1 * Vpc * 0.5
            Vpcm = 0.1 * Vpc
        elif Vpc > 2000:
            Cdm = 100.0
            Vpcm = 200.0
        CNRdm = Cdm / 24 / 0.2
        Armazdm = CNRdm * 3

        # 2. Cálculos de Pior Caso por Localidade
        Cdpc1, Cdpc2, Cdpc3 = 0.0, 0.0, 0.0
        if "Zona Costeira" in local:
            if Vpc >= 15200:
                Cdpc1, Cdpc2, Cdpc3 = 2400.0, 4800.0, 8000.0
            else:
                Cdpc1, Cdpc2, Cdpc3 = 0.15 * Vpc, 0.3 * Vpc, 0.55 * Vpc
        elif "Rios" in local:
            Cdpc1, Cdpc2, Cdpc3 = 320.0, 640.0, 1140.0
        elif "Águas marítimas" in local:
            if Vpc >= 11200:
                Cdpc1, Cdpc2, Cdpc3 = 1600.0, 3200.0, 6400.0
            else:
                Cdpc1, Cdpc2, Cdpc3 = 0.15 * Vpc, 0.3 * Vpc, 0.55 * Vpc

        # Normalizações do VB
        if Cdpc1 <= Cdm: Cdpc1 = Cdm
        if Cdpc2 <= Cdpc1: Cdpc2 = Cdpc1
        if Cdpc3 <= Cdpc2: Cdpc3 = Cdpc2

        CNRdpc1 = Cdpc1 / 24 / 0.2
        CNRdpc2 = Cdpc2 / 24 / 0.2
        CNRdpc3 = Cdpc3 / 24 / 0.2

        Armazdpc1 = CNRdpc1 * 3
        Armazdpc2 = CNRdpc2 * 3
        Armazdpc3 = CNRdpc3 * 3

        # 3. Cálculos de Barreiras
        Cerco = round(3 * comprimento)
        
        # Determinação das barreiras de contenção da mancha (Cont3) baseado no CNRdpc3
        if CNRdpc3 <= 50: Cont3 = 100.0
        elif CNRdpc3 <= 100: Cont3 = 200.0
        elif CNRdpc3 <= 200: Cont3 = 250.0
        elif CNRdpc3 <= 250: Cont3 = 300.0
        else: Cont3 = 400.0

        # Barreiras de Proteção
        if 3.5 * largura >= (1.5 + velocidade) * largura:
            Protecao = round(3.5 * largura)
        else:
            Protecao = round((1.5 + velocidade) * largura)
        if Protecao >= 350: Protecao = 350.0

        # Absorventes Totais
        Absorventes_total = Cerco + Cont3 + Protecao + linha_protecao

        # --- EXIBIÇÃO DOS RESULTADOS (Substituindo o Form2) ---
        # Em vez de apenas jogar o texto, use um container para agrupar visualmente
        with st.container(border=True):
            st.subheader("Resultados do Dimensionamento Mínimo")
            
            col_a, col_b = st.columns(2)
            col_a.metric("Volume de Pior Caso Calculado (Vpc)", f"{Vpc:.4f} m³")
            col_b.info(f"**Ambiente:** {local}")

        # Aba de Barreiras e Materiais
        st.subheader("Barreiras e Materiais Absorventes")
        df_barreiras = pd.DataFrame({
            "Item": [
                "Barreiras de Cerco (m)", "Barreiras de Contenção da Mancha (m)", 
                "Barreiras de Proteção (m)", "Barreiras para Áreas Sensíveis (m)",
                "Barreiras Absorventes Totais (m)", "Mantas Absorventes (unid/m)"
            ],
            "Quantidade Mínima": [Cerco, Cont3, Protecao, linha_protecao, Absorventes_total, Absorventes_total]
        })
        st.table(df_barreiras)

        # Aba de Recolhedores (Substituindo a DataGridView do Form2)
        st.subheader("Capacidade de Recolhimento e Armazenamento Temporário")
        
        if Vpc <= 8:
            dados_recolhedores = {
                "Classe de Descarga": ["Pequena", "Média", "Pior Caso (Nível 1)", "Pior Caso (Nível 2)", "Pior Caso (Nível 3)"],
                "Volume da Mancha": [f"{Vpc:.2f} m³", "-", "-", "-", "-"],
                "Tempo Limite": ["Até 2h", "-", "-", "-", "-"],
                "Capac. Recolhimento Diário": [f"{Vpc:.2f} m³/dia", "-", "-", "-", "-"],
                "Capac. Nominal Mínima (CNR)": [f"{CNRdp:.2f} m³/h", "-", "-", "-", "-"],
                "Armazenamento Temporário": [f"{Armazdp:.2f} m³", "-", "-", "-", "-"]
            }
        else:
            dados_recolhedores = {
                "Classe de Descarga": ["Pequena", "Média", "Pior Caso (Nível 1)", "Pior Caso (Nível 2)", "Pior Caso (Nível 3)"],
                "Volume da Mancha": [f"8.00 m³", f"{Vpcm:.2f} m³", f"{Vpc:.2f} m³", f"{Vpc:.2f} m³", f"{Vpc:.2f} m³"],
                "Tempo Limite": ["Até 2h", "Até 6h", "Até 12h", "Até 36h", "Até 60h"],
                "Capac. Recolhimento Diário": [f"8.00 m³/dia", f"{Cdm:.2f} m³/dia", f"{Cdpc1:.2f} m³/dia", f"{Cdpc2:.2f} m³/dia", f"{Cdpc3:.2f} m³/dia"],
                "Capac. Nominal Mínima (CNR)": [f"{CNRdp:.2f} m³/h", f"{CNRdm:.2f} m³/h", f"{CNRdpc1:.2f} m³/h", f"{CNRdpc2:.2f} m³/h", f"{CNRdpc3:.2f} m³/h"],
                "Armazenamento Temporário": [f"{Armazdp:.2f} m³", f"{Armazdm:.2f} m³", f"{Armazdpc1:.2f} m³", f"{Armazdpc2:.2f} m³", f"{Armazdpc3:.2f} m³"]
            }
            
        st.dataframe(pd.DataFrame(dados_recolhedores), hide_index=True)
