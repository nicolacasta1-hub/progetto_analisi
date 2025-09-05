# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

# Importiamo le funzioni dal nostro "cervello"
from analysis_logic import (
    arricchisci_dati_base, 
    calcola_kpi_globali,
    prepara_dati_trimestrali_annuali,
    prepara_dati_categorie,
    prepara_dati_top_flop,
    prepara_dati_trend_prodotto
)

# --- IMPOSTAZIONI PAGINA E STILE ---
st.set_page_config(layout="wide", page_title="Decision Intelligence Dashboard")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

local_css("style.css")

# Definiamo la nostra palette di colori obiettivo
COLOR_PALETTE = ["#007BFF", "#00C49F", "#FFBB28", "#FF8042", "#AF19FF"]

# --- FUNZIONE DI CARICAMENTO DATI ---
@st.cache_data
def load_data(file):
    try:
        df = pd.read_excel(file)
        return df
    except Exception as e:
        st.error(f"Errore nel caricamento del file: {e}")
        return None

# --- STATO DELL'APPLICAZIONE ---
if 'df' not in st.session_state:
    st.session_state['df'] = None

# --- SIDEBAR DI NAVIGAZIONE ---
with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=["Caricamento Dati", "Dashboard Globale", "Analisi Prodotti"],
        icons=["cloud-upload", "house", "box-seam"],
        menu_icon="cast",
        default_index=0,
    )
    # Altre sezioni verranno sviluppate in futuro
    # with st.expander...

# --- LOGICA DELLE PAGINE ---

if selected == "Caricamento Dati":
    st.title("Caricamento Dati e Contesto Aziendale")
    uploaded_file = st.file_uploader(
        "Scegli un file Excel per iniziare", 
        type="xlsx",
        key='file_uploader'
    )
    if uploaded_file is not None:
        st.session_state['df'] = load_data(uploaded_file)
        if st.session_state['df'] is not None:
            st.success("File caricato e processato con successo! Naviga alla Dashboard Globale per iniziare l'analisi.")

if selected == "Dashboard Globale":
    st.title("Global Dashboard 📈")
    
    if st.session_state['df'] is None:
        st.warning("Per favore, carica un file di dati nella sezione 'Caricamento Dati' per iniziare.")
    else:
        df_originale = st.session_state['df']
        
        periodo_selezionato = st.selectbox(
            "Seleziona Periodo di Analisi",
            options=['Anno Intero', 'Q1', 'Q2', 'Q3', 'Q4'],
            key='period_selector'
        )

        # Logica di calcolo dinamica
        kpi_precedenti_dict = None
        df_corrente = None
        
        if periodo_selezionato == 'Anno Intero':
            colonne_correnti = ['Vendite_Q1', 'Vendite_Q2', 'Vendite_Q3', 'Vendite_Q4']
            df_corrente = arricchisci_dati_base(df_originale, colonne_correnti)
        else:
            q_corrente_str = f'Vendite_{periodo_selezionato}'
            df_corrente = arricchisci_dati_base(df_originale, [q_corrente_str])
            
            q_num = int(periodo_selezionato[1])
            if q_num > 1:
                q_precedente_str = f'Vendite_Q{q_num - 1}'
                df_precedente = arricchisci_dati_base(df_originale, [q_precedente_str])
                kpi_precedenti_dict = calcola_kpi_globali(df_precedente)

        kpi_correnti_dict = calcola_kpi_globali(df_corrente)
        
        # --- KPI CARDS CON TREND ---
        st.divider()
        kpi_cols = st.columns(4)
        
        # Calcolo del delta per il primo KPI (Ricavi)
        delta_ricavi = None
        if kpi_precedenti_dict:
            if kpi_precedenti_dict['Ricavi Totali'] != 0:
                delta_ricavi = (kpi_correnti_dict['Ricavi Totali'] - kpi_precedenti_dict['Ricavi Totali']) / kpi_precedenti_dict['Ricavi Totali']
        
        kpi_cols[0].metric(label=f"Ricavi Totali ({periodo_selezionato})", value=f"€ {kpi_correnti_dict['Ricavi Totali']:.2f}", delta=f"{delta_ricavi:.1%}" if delta_ricavi is not None else None)
        kpi_cols[1].metric(label=f"Margine Totale ({periodo_selezionato})", value=f"€ {kpi_correnti_dict['Margine di Contribuzione Totale']:.2f}")
        kpi_cols[2].metric(label=f"Profitto Lordo Medio ({periodo_selezionato})", value=f"{kpi_correnti_dict['Profitto Lordo Medio (%)']:.1f} %")
        kpi_cols[3].metric(label=f"Unità Vendute ({periodo_selezionato})", value=f"{kpi_correnti_dict['Unità Vendute']}")
        st.divider()

        # --- GRAFICI ---
        if periodo_selezionato == 'Anno Intero':
            st.header("Visualizzazioni Annuali")
            dati_chart_trimestri = prepara_dati_trimestrali_annuali(df_originale)
            fig_trimestri = px.bar(dati_chart_trimestri, x='Trimestre', y='Ricavi', title='Andamento Performance Annuale', color_discrete_sequence=COLOR_PALETTE)
            fig_trimestri.add_scatter(x=dati_chart_trimestri['Trimestre'], y=dati_chart_trimestri['Profittabilità (%)'], mode='lines', name='Profittabilità (%)', yaxis='y2')
            fig_trimestri.update_layout(yaxis2=dict(title='Profittabilità (%)', overlaying='y', side='right'), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_trimestri, use_container_width=True)

        st.header(f"Analisi di Dettaglio per il Periodo: {periodo_selezionato}")
        incidenza_ricavi, incidenza_margine = prepara_dati_categorie(df_corrente)
        col_graf_1, col_graf_2 = st.columns(2)
        with col_graf_1:
            fig_torta_ricavi = px.pie(incidenza_ricavi, names='Categoria', values='Ricavo Totale', title='Incidenza Ricavi per Categoria', hole=0.4, color_discrete_sequence=COLOR_PALETTE)
            st.plotly_chart(fig_torta_ricavi, use_container_width=True)
        with col_graf_2:
            fig_torta_margine = px.pie(incidenza_margine, names='Categoria', values='Margine Totale', title='Incidenza Margine per Categoria', hole=0.4, color_discrete_sequence=COLOR_PALETTE)
            st.plotly_chart(fig_torta_margine, use_container_width=True)

        st.divider()
        top_10, flop_10 = prepara_dati_top_flop(df_corrente)
        col_top, col_flop = st.columns(2)
        with col_top:
            fig_top = px.bar(top_10, x='Margine Totale', y='Nome Piatto', orientation='h', title='Top 10 Prodotti per Margine', color_discrete_sequence=px.colors.sequential.Greens_r)
            fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_top, use_container_width=True)
        with col_flop:
            fig_flop = px.bar(flop_10, x='Margine Totale', y='Nome Piatto', orientation='h', title='Flop 10 Prodotti per Margine', color_discrete_sequence=px.colors.sequential.Reds_r)
            fig_flop.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_flop, use_container_width=True)

if selected == "Analisi Prodotti":
    st.title("Analisi Dettagliata per Prodotto 🔎")
    if st.session_state['df'] is None:
        st.warning("Per favore, carica un file di dati nella sezione 'Caricamento Dati' per iniziare.")
    else:
        df_originale = st.session_state['df']
        lista_prodotti = sorted(df_originale['Nome Piatto'].unique().tolist())
        prodotto_selezionato = st.selectbox("Seleziona un Prodotto:", options=lista_prodotti)
        
        if prodotto_selezionato:
            dati_trend_prodotto = prepara_dati_trend_prodotto(df_originale, prodotto_selezionato)
            fig_trend = px.line(dati_trend_prodotto, x='Trimestre', y='Quantita Vendute', 
                                title=f"Andamento Trimestrale Vendite: {prodotto_selezionato}", markers=True)
            st.plotly_chart(fig_trend, use_container_width=True)