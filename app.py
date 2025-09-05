# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

# Importiamo le nostre funzioni dal "cervello"
from analysis_logic import (
    arricchisci_dati_base, 
    calcola_kpi_globali,
    prepara_dati_trimestrali,
    prepara_dati_categorie,
    prepara_dati_top_flop
)

# --- IMPOSTAZIONI PAGINA E STILE ---
st.set_page_config(layout="wide", page_title="Decision Intelligence Dashboard")

# Funzione per caricare il nostro file CSS personalizzato
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Carichiamo lo stile (assicurati di avere style.css e .streamlit/config.toml)
local_css("style.css")

# Definiamo la nostra palette di colori obiettivo
COLOR_PALETTE = ["#007BFF", "#00C49F", "#FFBB28", "#FF8042", "#AF19FF"]

# --- FUNZIONE DI CARICAMENTO DATI ---
@st.cache_data
def carica_dati(file_caricato):
    df = pd.read_excel(file_caricato)
    return df

# --- SIDEBAR DI NAVIGAZIONE ---
with st.sidebar:
    #st.image("logo_placeholder.png", width=100) # Assicurati di avere un'immagine logo
    selected = option_menu(
        menu_title="Menu Principale",
        options=["Dashboard Globale", "Analisi Categorie", "Analisi Prodotti", "Analisi Comparativa", "Laboratorio Interattivo", "Assistente AI"],
        icons=["house", "pie-chart", "box-seam", "intersect", "magic", "robot"],
        menu_icon="cast",
        default_index=0,
    )
    # L'assistente AI sarà in un expander per essere nascondibile
    with st.expander("🤖 Assistente AI"):
        st.write("Qui ci sarà la nostra interfaccia di chat!")
        # st.text_input(...) e logica IA

# --- CORPO PRINCIPALE DELL'APP ---

# Per ora, mostriamo solo il contenuto della Dashboard Globale
if selected == "Dashboard Globale":

    st.title("Global Dashboard 📈")

    uploaded_file = st.file_uploader(
        "Scegli un file Excel con i dati di vendita (deve contenere la colonna 'Data Vendita')", 
        type="xlsx"
    )
    
    if uploaded_file is not None:
        
        df_grezzo = carica_dati(uploaded_file)
        df_analisi = arricchisci_dati_base(df_grezzo)
        
        # --- FILTRO PERIODO ---
        st.header("Filtra per Periodo")
        lista_trimestri = ['Tutti'] + sorted(df_analisi['Trimestre'].unique().tolist())
        periodo_selezionato = st.selectbox("Scegli un Trimestre da analizzare:", options=lista_trimestri)

        # Filtriamo i dati in base alla selezione
        if periodo_selezionato == 'Tutti':
            df_filtrato = df_analisi
        else:
            df_filtrato = df_analisi[df_analisi['Trimestre'] == periodo_selezionato]
        
        # --- KPI GLOBALI ---
        kpi_globali = calcola_kpi_globali(df_filtrato)
        
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        # (Codice KPI come prima, ma usando i dati filtrati)
        with col1: st.metric(label="Ricavi Totali", value=f"€ {kpi_globali['Ricavi Totali']:.2f}")
        with col2: st.metric(label="Margine Totale", value=f"€ {kpi_globali['Margine di Contribuzione Totale']:.2f}")
        with col3: st.metric(label="Profitto Lordo Medio", value=f"{kpi_globali['Profitto Lordo Medio (%)']:.1f} %")
        with col4: st.metric(label="Unità Vendute", value=f"{kpi_globali['Unità Vendute']}")
        st.divider()

        # --- GRAFICI ---
        st.header("Visualizzazioni")
        
        col_graf_1, col_graf_2 = st.columns([2, 1]) # La prima colonna è più grande

        with col_graf_1:
            # Grafico trimestrale (usa i dati non filtrati per mostrare sempre il trend annuale)
            dati_chart_trimestri = prepara_dati_trimestrali(df_analisi)
            fig_trimestri = px.bar(dati_chart_trimestri, x='Trimestre', y='Ricavi', 
                                   title='Andamento Trimestrale Ricavi', color_discrete_sequence=COLOR_PALETTE)
            fig_trimestri.add_scatter(x=dati_chart_trimestri['Trimestre'], y=dati_chart_trimestri['Profittabilità (%)'], 
                                      mode='lines', name='Profittabilità (%)', yaxis='y2')
            fig_trimestri.update_layout(yaxis2=dict(title='Profittabilità (%)', overlaying='y', side='right'))
            st.plotly_chart(fig_trimestri, use_container_width=True)

        with col_graf_2:
            incidenza_ricavi, marginalita_media = prepara_dati_categorie(df_filtrato)
            # Grafico a torta per l'incidenza dei ricavi
            fig_torta = px.pie(incidenza_ricavi, names='Categoria', values='Ricavo Totale', 
                               title='Incidenza Ricavi per Categoria', hole=0.4, color_discrete_sequence=COLOR_PALETTE)
            st.plotly_chart(fig_torta, use_container_width=True)

        st.divider()

        # Grafici Top/Flop
        col_top, col_flop = st.columns(2)
        top_10, flop_10 = prepara_dati_top_flop(df_filtrato)

        with col_top:
            fig_top = px.bar(top_10, x='Margine Totale', y='Piatto', orientation='h', 
                             title='Top 10 Prodotti per Margine', color_discrete_sequence=px.colors.sequential.Greens_r)
            st.plotly_chart(fig_top, use_container_width=True)
            
        with col_flop:
            fig_flop = px.bar(flop_10, x='Margine Totale', y='Piatto', orientation='h',
                              title='Flop 10 Prodotti per Margine', color_discrete_sequence=px.colors.sequential.Reds_r)
            st.plotly_chart(fig_flop, use_container_width=True)

    else:
        st.info("In attesa del caricamento di un file Excel per avviare l'analisi.")