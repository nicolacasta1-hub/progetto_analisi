# app.py

import streamlit as st
import pandas as pd
from analysis_logic import arricchisci_dati_base, calcola_kpi_globali

# --- IMPOSTAZIONI PAGINA E STILE ---
st.set_page_config(layout="wide", page_title="Analisi Strategica Vendite")

# Funzione per caricare il nostro file CSS personalizzato
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# Carichiamo lo stile
local_css("style.css")


# --- FUNZIONE DI CARICAMENTO DATI CON CACHE ---
@st.cache_data
def carica_dati(file_caricato):
    df = pd.read_excel(file_caricato)
    return df

# --- INTESTAZIONE E UPLOADER ---
st.title("Global Dashboard 📈")

uploaded_file = st.file_uploader(
    "Scegli un file Excel con i dati di vendita", 
    type="xlsx"
)

# --- CORPO PRINCIPALE DELL'APP ---
if uploaded_file is not None:
    
    df_grezzo = carica_dati(uploaded_file)
    df_analisi = arricchisci_dati_base(df_grezzo)
    kpi_globali = calcola_kpi_globali(df_analisi)
    
    st.divider()
    
    # --- SEZIONE KPI CON STILE PERSONALIZZATO ---
    
    # Creiamo 4 colonne per i nostri 4 KPI
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Ricavi Totali",
            value=f"€ {kpi_globali['Ricavi Totali']:.2f}"
        )
    
    with col2:
        st.metric(
            label="Margine di Contribuzione Totale",
            value=f"€ {kpi_globali['Margine di Contribuzione Totale']:.2f}"
        )
        
    with col3:
        st.metric(
            label="Profitto Lordo Medio",
            value=f"{kpi_globali['Profitto Lordo Medio (%)']:.1f} %"
        )
        
    with col4:
        st.metric(
            label="Unità Totali Vendute",
            value=f"{kpi_globali['Unità Vendute']}"
        )
    
    st.divider()
    
    st.header("Dati di Dettaglio")
    st.dataframe(df_analisi)

else:
    st.info("In attesa del caricamento di un file Excel per avviare l'analisi.")
