# app.py

import streamlit as st
import pandas as pd
from logic.logic_core import arricchisci_dati_base
from utils import local_css
# --- IMPOSTAZIONI PAGINA E STILE ---
# Questa configurazione verrà applicata a tutte le pagine
st.set_page_config(
    layout="wide", 
    page_title="Decision Intelligence Dashboard",
    initial_sidebar_state="expanded"
)

# Assicurati che i file style.css e .streamlit/config.toml siano presenti
local_css("style.css")

# --- STATO DELL'APPLICAZIONE (MEMORIA CONDIVISA) ---
# Inizializziamo lo stato della sessione per conservare i dati tra le pagine
if 'df' not in st.session_state:
    st.session_state['df'] = None

# --- PAGINA DI CARICAMENTO DATI ---
# Questo file ora gestisce solo la pagina principale.
# La navigazione è gestita automaticamente da Streamlit.
st.title("Caricamento Dati e Contesto Aziendale")
st.info("Benvenuto. Per iniziare, carica un file Excel contenente i dati di vendita.")

uploaded_file = st.file_uploader(
    "Scegli un file Excel", 
    type="xlsx",
    key='file_uploader'
)

st.divider()
st.subheader("Inserimento Costi Fissi")
costi_fissi_input = st.number_input(
    "Inserisci i Costi Fissi totali per il periodo analizzato (€)",
    min_value=0.0,
    value=5000.0,  # Valore di default per mostrare un esempio
    step=100.0,
    help="Inserisci qui la somma di tutti i costi che non variano con le vendite (es. affitto, stipendi, utenze)."
)

# Aggiorniamo lo stato della sessione con il valore inserito
st.session_state['costi_fissi'] = costi_fissi_input
st.divider()
if uploaded_file is not None:
    try:
        df_raw = pd.read_excel(uploaded_file)
        # Salviamo il DataFrame arricchito con i dati ANNUALI nello stato della sessione
        st.session_state['df'] = arricchisci_dati_base(df_raw)
        st.success("File caricato e processato con successo! Seleziona una pagina dal menu a sinistra per iniziare l'analisi.")
    except Exception as e:
        st.error(f"Errore nel processare il file: Assicurati che le colonne siano corrette. Dettaglio: {e}")