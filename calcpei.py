import streamlit as st
import pandas as pd
import math

def fmt_br(valor, casas=2):
    """Formata um número para o padrão brasileiro (ex: 1.234,56)"""
    if valor is None:
        return "-"
    # Formata no padrão americano com vírgula no milhar: 1,234,567.89
    string_formatada = f"{valor:,.{casas}f}"
    # Inverte os separadores usando um marcador temporário
    return string_formatada.replace(",", "TEMP").replace(".", ",").replace("TEMP", ".")

# Configuração inicial da página
st.set_page_config(page_title="CalcPEI - Mac & Nuvem", page_icon="💧", layout="wide")

st.title("Calculadora PEI (CalcPEI)")
st.caption("Dimensionamento de Capacidade Mínima de Resposta - Resolução CONAMA nº 398/2008")

# --- FORÇAR CENTRALIZAÇÃO E ESTILO DOS CABEÇALHOS DAS TABELAS ---
st.markdown("""
    <style>
    /* Centraliza todas as células e cabeçalhos */
    [data-testid="stTable"] th, [data-testid="stTable"] td {
        text-align: center !important;
    }
    /* Destaca o cabeçalho com fundo verde musgo do Ibama e texto branco */
    [data-testid="stTable"] th {
        background-color: #2A5C34 !important;
        color: #FFFFFF !important;
    }
    </style>
""", unsafe_allow_html=True)

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
    v1a = st.sidebar.number_input(
        "Volume V1 (m³):", 
        min_value=0.0, 
        value=0.0, 
        step=1.0,
        help="""
        **Volume correspondente à descarga de pior caso** $Vpc = V1$, onde:  
        
        * **Vpc** — volume do derramamento correspondente à descarga de pior caso  
        * **V1** — capacidade máxima do tanque, equipamento de processo ou reservatório de maior capacidade (1)  
        
        *(1) No caso de tanques que operem equalizados, deverá ser considerada a soma da capacidade máxima dos tanques.*
        """
    )
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

# --- PASSO 3: BOTÃO DE CÁLCULO E LÓGICA MATEMÁTICA ---
if st.sidebar.button("Calcular Dimensionamento", type="primary"):
    
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
        
        if CNRdpc3 <= 50: Cont3 = 100.0
        elif CNRdpc3 <= 100: Cont3 = 200.0
        elif CNRdpc3 <= 200: Cont3 = 250.0
        elif CNRdpc3 <= 250: Cont3 = 300.0
        else: Cont3 = 400.0

        if 3.5 * largura >= (1.5 + velocidade) * largura:
            Protecao = round(3.5 * largura)
        else:
            Protecao = round((1.5 + velocidade) * largura)
        if Protecao >= 350: Protecao = 350.0

        Absorventes_total = Cerco + Cont3 + Protecao + linha_protecao

        # --- EXIBIÇÃO DOS RESULTADOS FORMATADOS ---
        with st.container(border=True):
            st.header("Resultados do Dimensionamento Mínimo")
            
            col_a, col_b = st.columns(2)
            # Aplicando a formatação BR com 4 casas decimais para o VPC como estava no VB
            col_a.metric("Volume de Pior Caso Calculado (Vpc)", f"{fmt_br(Vpc, 4)} m³")
            col_b.markdown(f"""
                <div style="background-color: #EBF5EE; color: #2A5C34; padding: 15px; border-radius: 0.5rem; border-left: 5px solid #2A5C34; font-size: 1rem; line-height: 1.5;">
                    <strong>Ambiente:</strong> {local}
                </div>
            """, unsafe_allow_html=True)

            # --- TABELA 1: BARREIRAS ---
            st.subheader("Barreiras e Materiais Absorventes")
            
            df_barreiras = pd.DataFrame({
                "Item": [
                    "Barreiras de Cerco (m)", "Barreiras de Contenção da Mancha (m)", 
                    "Barreiras de Proteção (m)", "Barreiras para Áreas Sensíveis (m)",
                    "Barreiras Absorventes Totais (m)", "Mantas Absorventes (unid/m)"
                ],
                "Quantidade Mínima": [
                    fmt_br(Cerco, 0), fmt_br(Cont3, 0), fmt_br(Protecao, 0), 
                    fmt_br(linha_protecao, 0), fmt_br(Absorventes_total, 0), fmt_br(Absorventes_total, 0)
                ]
            })
            
            # O CSS global do topo já vai centralizar automaticamente aqui
            st.table(df_barreiras)

            # --- TABELA 2: RECOLHEDORES ---
            st.subheader("Capacidade de Recolhimento e Armazenamento Temporário")
            
            if Vpc <= 8:
                dados_recolhedores = {
                    "Classe de Descarga": ["Pequena", "Média", "Pior Caso (Nível 1)", "Pior Caso (Nível 2)", "Pior Caso (Nível 3)"],
                    "Volume da Mancha": [f"{fmt_br(Vpc)} m³", "-", "-", "-", "-"],
                    "Tempo Limite": ["Até 2h", "-", "-", "-", "-"],
                    "Capac. Recolhimento Diário": [f"{fmt_br(Vpc)} m³/dia", "-", "-", "-", "-"],
                    "Capac. Nominal Mínima (CNR)": [f"{fmt_br(CNRdp)} m³/h", "-", "-", "-", "-"],
                    "Armazenamento Temporário": [f"{fmt_br(Armazdp)} m³", "-", "-", "-", "-"]
                }
            else:
                dados_recolhedores = {
                    "Classe de Descarga": ["Pequena", "Média", "Pior Caso (Nível 1)", "Pior Caso (Nível 2)", "Pior Caso (Nível 3)"],
                    "Volume da Mancha": ["8,00 m³", f"{fmt_br(Vpcm)} m³", f"{fmt_br(Vpc)} m³", f"{fmt_br(Vpc)} m³", f"{fmt_br(Vpc)} m³"],
                    "Tempo Limite": ["Até 2h", "Até 6h", "Até 12h", "Até 36h", "Até 60h"],
                    "Capac. Recolhimento Diário": ["8,00 m³/dia", f"{fmt_br(Cdm)} m³/dia", f"{fmt_br(Cdpc1)} m³/dia", f"{fmt_br(Cdpc2)} m³/dia", f"{fmt_br(Cdpc3)} m³/dia"],
                    "Capac. Nominal Mínima (CNR)": [f"{fmt_br(CNRdp)} m³/h", f"{fmt_br(CNRdm)} m³/h", f"{fmt_br(CNRdpc1)} m³/h", f"{fmt_br(CNRdpc2)} m³/h", f"{fmt_br(CNRdpc3)} m³/h"],
                    "Armazenamento Temporário": [f"{fmt_br(Armazdp)} m³", f"{fmt_br(Armazdm)} m³", f"{fmt_br(Armazdpc1)} m³", f"{fmt_br(Armazdpc2)} m³", f"{fmt_br(Armazdpc3)} m³"]
                }
                
            df_recolhedores = pd.DataFrame(dados_recolhedores)
            st.table(df_recolhedores)

# ==============================================================================
# SUBSTITUA O BLOCO DO POPOVER ANTERIOR POR ESTE:
# ==============================================================================
st.sidebar.markdown("---")
with st.sidebar.popover("📝 Ver Notas do Programa", use_container_width=True):
    st.markdown("""
    ### NOTAS

    **I -** Esse software contempla apenas o dimensionamento de materiais para capacidade mínima de resposta, conforme especificado na Resolução CONAMA nº 398/2008: barreiras de contenção, barreiras de absorção, mantas de absorção, materiais de absorção à granel, recolhedores e tanques de armazenamento temporário.

    **II -** Materiais complementares e acessórios, a exemplo de embarcações, barras de reboque (towbar), âncoras, veículos, sopradores, bombas, mangotes, cabos e etc., devem compor o Plano de Emergência Individual nos quantitativos suficientes para atender as estratégias de resposta e a realidade do local.

    **III -** A capacidade de resposta da instalação deverá ser assegurada por meio de recursos próprios ou de terceiros provenientes de acordos previamente firmados, obedecidos os critérios de descargas pequenas (8 m³) e médias (até 200 m³) e de pior caso.

    **IV -** O cálculo do volume da descarga de pior caso para a determinação da CEDRO requerida para plataformas deverá considerar o volume decorrente da perda de controle do poço durante 4 dias, demonstrando capacidade de manutenção da estrutura de resposta durante 30 dias, mantendo-se as demais orientações da seção 2.2.1 do Anexo II.

    **V -** Em portos organizados e demais instalações portuárias, e terminais, deverá ser incluído o cenário de derramamento de óleo por navios dentro dos seguintes limites:
    * **1 - Terminais de óleo:** a CEDRO deverá ser dimensionada para descargas pequena e média. No caso de derramamento de óleo acima de 200 m³, a instalação deverá apresentar as ações previstas para garantir a continuidade de resposta ao atendimento da emergência.  
    * **2 - Portos organizados, demais instalações portuárias e outros terminais:** a CEDRO deverá ser dimensionada para descarga pequena. No caso de derramamento de óleo acima de 8 m³, a instalação deverá apresentar as ações previstas para garantir a continuidade de resposta ao atendimento da emergência.  

    **VI -** As plataformas deverão estar equipadas com o conjunto de equipamentos e materiais estabelecidos inerentes ao Plano de Emergência de Navios para Poluição por Óleo (Shipboard Oil Pollution Emergency Plan - SOPEP, em inglês), conforme definido na Convenção Internacional para a Prevenção da Poluição Causada por Navios, concluída em Londres, em 2 de novembro de 1973, seu Protocolo, concluído em Londres, em 17 de fevereiro de 1998, suas Emendas de 1984 e seus anexos Operacionais III, IV e V, promulgada no Brasil por meio do Decreto nº 2.508, de 4 de março de 1998. Republicada por ter saído com incorreção, do original, no Diário Oficial da União de 27 de fevereiro de 2002, Seção 1, págs. 128 a 133.  

    **VII -** A expressão "1,5 + velocidade máxima da corrente em nós x largura do corpo hídrico, em metros", contida no Anexo III da Resolução CONAMA nº 398/2008, foi alterada neste software para "(1,5 + velocidade máxima da corrente em nós) x largura do corpo hídrico, em metros", por questão de coerência.  

    **VIII -** Recomenda-se leitura atenta da Resolução CONAMA nº 398/2008, para consideração de situações particulares especificadas.
    """)
st.sidebar.markdown("---")
