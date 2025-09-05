import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from analysis_logic import (
    arricchisci_dati_base,
    calcola_kpi_globali,
    prepara_dati_trimestrali_per_grafico_annuale,
    prepara_dati_categorie,
    prepara_dati_top_flop,
    genera_insight_kpi,
    genera_insight_strutturali
)

# --- CONFIGURAZIONE PAGINA E CSS ---
st.set_page_config(page_title="Decision Intelligence Dashboard", layout="wide")

def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style.css")

# --- GESTIONE DELLO STATO ---
if 'data' not in st.session_state:
    st.session_state.data = None
if 'business_context' not in st.session_state:
    st.session_state.business_context = ""

# --- SIDEBAR ---
with st.sidebar:
    selected = option_menu(
        menu_title="Menu Principale",
        options=["Caricamento Dati", "Dashboard Globale"],
        icons=["cloud-upload", "bar-chart-line"],
        menu_icon="cast",
        default_index=0
    )

# --- PAGINA: CARICAMENTO DATI ---
if selected == "Caricamento Dati":
    st.title("Caricamento e Contesto Aziendale")
    st.info("Inizia caricando il file Excel con i dati di vendita. Il file deve contenere le colonne specificate.")
    
    uploaded_file = st.file_uploader("Seleziona il file Excel", type=["xlsx"])
    
    if uploaded_file:
        try:
            st.session_state.data = pd.read_excel(uploaded_file)
            st.success("File caricato con successo! Passa al 'Dashboard Globale' per l'analisi.")
        except Exception as e:
            st.error(f"Errore nella lettura del file: {e}")
            st.session_state.data = None
            
    st.text_area(
        "Contesto Qualitativo (Opzionale)",
        value=st.session_state.business_context,
        height=150,
        help="Inserisci qui i tuoi obiettivi, punti di forza o debolezza. Questi dati verranno usati per arricchire le analisi.",
        key="business_context"
    )

# --- PAGINA: DASHBOARD GLOBALE ---
if selected == "Dashboard Globale":
    if st.session_state.data is None:
        st.warning("Nessun dato caricato. Per favore, vai alla pagina 'Caricamento Dati' e carica un file Excel.")
        st.stop()

    st.title("Dashboard Globale di Analisi Strategica")
    raw_df = st.session_state.data

    # --- SELETTORE DEL PERIODO ---
    selected_period = st.selectbox(
        "Seleziona Periodo di Analisi",
        options=['Anno Intero', 'Q1', 'Q2', 'Q3', 'Q4']
    )

    # --- LOGICA DI FILTRAGGIO E CALCOLO DINAMICO ---
    df_periodo, df_periodo_prec = None, None
    kpi_attuali, kpi_precedenti = None, None
    quarter_map = {'Q2': ['Vendite_Q1'], 'Q3': ['Vendite_Q2'], 'Q4': ['Vendite_Q3']}

    # Calcolo periodo corrente
    if selected_period == 'Anno Intero':
        cols_correnti = ['Vendite_Q1', 'Vendite_Q2', 'Vendite_Q3', 'Vendite_Q4']
    else:
        cols_correnti = [f'Vendite_{selected_period}']
    df_periodo = arricchisci_dati_base(raw_df, cols_correnti)
    kpi_attuali = calcola_kpi_globali(df_periodo)

    # Calcolo periodo precedente (se applicabile)
    if selected_period in quarter_map:
        cols_precedenti = quarter_map[selected_period]
        df_periodo_prec = arricchisci_dati_base(raw_df, cols_precedenti)
        kpi_precedenti = calcola_kpi_globali(df_periodo_prec)

    # --- SEZIONE KPI CON TREND ---
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Indicatori di Performance Chiave (KPIs)")
    kpi_cols = st.columns(4)
    
    kpi_names = list(kpi_attuali.keys())
    for i, col in enumerate(kpi_cols):
        with col:
            delta = None
            if kpi_precedenti:
                val_attuale = kpi_attuali[kpi_names[i]]
                val_precedente = kpi_precedenti[kpi_names[i]]
                if val_precedente != 0:
                    delta = f"{((val_attuale - val_precedente) / val_precedente) * 100:.1f}%"
            
            # Applica lo stile CSS tramite un contenitore
            with st.container():
                st.markdown(f'<div class="kpi-card">', unsafe_allow_html=True)
                st.metric(label=kpi_names[i], value=f"{kpi_attuali[kpi_names[i]]:,.2f}", delta=delta)
                st.markdown('</div>', unsafe_allow_html=True)


    # --- SEZIONE INSIGHTS AUTOMATICI ---
    st.subheader("Insight Strategici Automatici")
    insight_kpi = genera_insight_kpi(kpi_attuali, kpi_precedenti)
    if insight_kpi:
        st.warning(insight_kpi)

    df_annuale_completo = arricchisci_dati_base(raw_df, ['Vendite_Q1', 'Vendite_Q2', 'Vendite_Q3', 'Vendite_Q4'])
    insights_strutturali = genera_insight_strutturali(df_annuale_completo)
    for insight in insights_strutturali:
        st.info(insight)
    
    # --- GRAFICI ---
    st.markdown("<hr>", unsafe_allow_html=True)

    if selected_period == 'Anno Intero':
        st.subheader("Andamento Performance Annuale")
        df_trend = prepara_dati_trimestrali_per_grafico_annuale(raw_df)
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(x=df_trend['Trimestre'], y=df_trend['Ricavi'], name='Ricavi (€)', marker_color='#3498DB'))
        fig_trend.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', title_text='Ricavi per Trimestre')
        st.plotly_chart(fig_trend, use_container_width=True)

    st.subheader(f"Analisi dei Driver di Performance ({selected_period})")
    
    col1, col2 = st.columns(2)
    with col1:
        df_ricavi_cat, df_margine_cat = prepara_dati_categorie(df_periodo)
        fig_ric_cat = px.pie(df_ricavi_cat, names='Categoria', values='Ricavi', title='Incidenza Ricavi per Categoria', hole=0.4)
        fig_ric_cat.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_ric_cat, use_container_width=True)

    with col2:
        df_ricavi_cat, df_margine_cat = prepara_dati_categorie(df_periodo)
        fig_mar_cat = px.pie(df_margine_cat, names='Categoria', values='Margine', title='Incidenza Margine per Categoria', hole=0.4)
        fig_mar_cat.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_mar_cat, use_container_width=True)

    st.subheader(f"Analisi di Portafoglio Prodotto ({selected_period})")
    col3, col4 = st.columns(2)
    with col3:
        df_top, df_flop = prepara_dati_top_flop(df_periodo)
        fig_top = px.bar(df_top, x='Margine Totale', y='Nome Piatto', orientation='h', title='Top 10 Prodotti per Margine Totale')
        fig_top.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_top, use_container_width=True)
    with col4:
        df_top, df_flop = prepara_dati_top_flop(df_periodo)
        fig_flop = px.bar(df_flop, x='Margine Totale', y='Nome Piatto', orientation='h', title='Flop 10 Prodotti per Margine Totale')
        fig_flop.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig_flop, use_container_width=True)