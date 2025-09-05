import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
# Importazioni dal file di logica di analisi
from analysis_logic import (
    arricchisci_dati_base,
    calcola_kpi_globali,
    prepara_dati_trimestrali_per_grafico_annuale,
    prepara_dati_categorie,
    prepara_dati_top_flop
)

# Importazioni dal nuovo file di logica degli insight
from insights_logic import (
    analizza_kpi_trends,
    analizza_struttura_business
)

# --- CONFIGURAZIONE PAGINA E CSS ---
st.set_page_config(page_title="Decision Intelligence Dashboard", layout="wide")

def local_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"File CSS '{file_name}' non trovato. Assicurati che sia nella stessa cartella di 'app.py'.")

local_css("style.css")

# --- GESTIONE DELLO STATO ---
if 'df' not in st.session_state:
    st.session_state['df'] = None

# --- SIDEBAR ---
with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=["Caricamento Dati", "Dashboard Globale", "Analisi Categorie", "Analisi Prodotti", "Analisi Comparativa", "Laboratorio Interattivo"],
        icons=["cloud-upload", "bar-chart-line", "pie-chart", "list-task", "braces", "tools"],
        menu_icon="robot",
        default_index=0
    )
    st.sidebar.markdown("---")
    with st.sidebar.expander("Assistente AI (in sviluppo)"):
        st.info("Una futura versione integrerà un assistente conversazionale per porre domande dirette sui dati.")

# --- PAGINA: CARICAMENTO DATI ---
if selected == "Caricamento Dati":
    st.title("Caricamento Dati e Contesto Aziendale")
    st.info("Inizia caricando il file Excel con i dati di vendita.")
    
    uploaded_file = st.file_uploader("Seleziona il file .xlsx", type=["xlsx"])
    
    if uploaded_file:
        try:
            st.session_state['df'] = pd.read_excel(uploaded_file)
            st.success("File caricato con successo! Passa al 'Dashboard Globale' per l'analisi.")
        except Exception as e:
            st.error(f"Errore nella lettura del file: {e}")
            st.session_state['df'] = None
            
    st.text_area(
        "Contesto Aziendale (Opzionale)",
        "Inserisci qui i tuoi obiettivi, punti di forza o debolezza.",
        height=150,
        key="business_context"
    )

# --- PAGINA: DASHBOARD GLOBALE ---
if selected == "Dashboard Globale":
    if st.session_state['df'] is None:
        st.warning("Nessun dato caricato. Per favore, vai alla pagina 'Caricamento Dati' e carica un file Excel.")
        st.stop()

    st.title("Dashboard Globale di Analisi Strategica")
    raw_df = st.session_state['df']

    selected_period = st.selectbox(
        "Seleziona Periodo di Analisi",
        options=['Anno Intero', 'Q1', 'Q2', 'Q3', 'Q4']
    )
    st.markdown('<div class="dashboard-container">', unsafe_allow_html=True)

    # --- LOGICA DI CALCOLO DINAMICO ---
    kpi_precedenti = None
    quarter_map = {'Q2': ['Vendite_Q1'], 'Q3': ['Vendite_Q2'], 'Q4': ['Vendite_Q3']}
    
    if selected_period == 'Anno Intero':
        cols_correnti = ['Vendite_Q1', 'Vendite_Q2', 'Vendite_Q3', 'Vendite_Q4']
    else:
        cols_correnti = [f'Vendite_{selected_period}']

    df_periodo = arricchisci_dati_base(raw_df, cols_correnti)
    kpi_attuali = calcola_kpi_globali(df_periodo)

    if selected_period in quarter_map:
        cols_precedenti = quarter_map[selected_period]
        df_periodo_prec = arricchisci_dati_base(raw_df, cols_precedenti)
        kpi_precedenti = calcola_kpi_globali(df_periodo_prec)

    # --- SEZIONE KPI CON TREND ---
    st.markdown("<hr>", unsafe_allow_html=True)
    kpi_cols = st.columns(4)
    kpi_names = list(kpi_attuali.keys())
    
    for i, col in enumerate(kpi_cols):
        with col:
            delta = None
            if kpi_precedenti:
                val_attuale = kpi_attuali[kpi_names[i]]
                val_precedente = kpi_precedenti[kpi_names[i]]
                if val_precedente != 0:
                    delta_val = ((val_attuale - val_precedente) / val_precedente) * 100
                    delta = f"{delta_val:.1f}%"
            
            val_formattato = f"€ {kpi_attuali[kpi_names[i]]:,.0f}" if "€" in kpi_names[i] or "Ricavi" in kpi_names[i] or "Margine" in kpi_names[i] else f"{kpi_attuali[kpi_names[i]]:,.0f}"
            if "%" in kpi_names[i]: val_formattato = f"{kpi_attuali[kpi_names[i]]:.1f}%"
            
            st.metric(label=kpi_names[i], value=val_formattato, delta=delta)
    
    # --- SEZIONE INSIGHTS AUTOMATICI ---
st.subheader("Insight Strategici")

# Insight basati sul trend (Livello 1)
insight_trend = analizza_kpi_trends(kpi_attuali, kpi_precedenti)
if insight_trend:
    # Usiamo st.warning per evidenziare i trend che richiedono attenzione
    st.warning(insight_trend[0])

# Insight basati sulla struttura del business (Livello 2 e 3)
# Calcoliamo i dati annuali arricchiti solo se necessario
df_annuale_arricchito = arricchisci_dati_base(raw_df, ['Vendite_Q1', 'Vendite_Q2', 'Vendite_Q3', 'Vendite_Q4'])
insights_strutturali = analizza_struttura_business(df_annuale_arricchito)

if insights_strutturali:
    with st.container(border=True):
        for insight in insights_strutturali:
            st.info(insight) # Usiamo st.info per gli insight strutturali
    
    st.markdown("<hr>", unsafe_allow_html=True)

    # --- GRAFICO CONDIZIONALE ---
    if selected_period == 'Anno Intero':
        st.subheader("Andamento Performance Annuale")
        df_trend = prepara_dati_trimestrali_per_grafico_annuale(raw_df)
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Bar(x=df_trend['Trimestre'], y=df_trend['Ricavi'], name='Ricavi (€)', marker_color='#007BFF'))
        fig_trend.add_trace(go.Scatter(x=df_trend['Trimestre'], y=df_trend['Profittabilità (%)'], name='Profittabilità (%)', mode='lines+markers', yaxis="y2"))
        fig_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            yaxis=dict(showgrid=False), yaxis2=dict(title="Profittabilità (%)", overlaying="y", side="right", showgrid=False)
        )
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- ALTRI GRAFICI ---
    st.subheader(f"Analisi dei Driver di Performance ({selected_period})")
    col1, col2 = st.columns(2)
    with col1:
        df_ricavi_cat, _ = prepara_dati_categorie(df_periodo)
        fig_ric_cat = px.pie(df_ricavi_cat, names='Categoria', values='Ricavi', title='Incidenza Ricavi per Categoria', hole=0.4)
        fig_ric_cat.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_ric_cat, use_container_width=True)
    with col2:
        _, df_margine_cat = prepara_dati_categorie(df_periodo)
        fig_mar_cat = px.pie(df_margine_cat, names='Categoria', values='Margine', title='Incidenza Margine per Categoria', hole=0.4)
        fig_mar_cat.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False)
        st.plotly_chart(fig_mar_cat, use_container_width=True)

    st.subheader(f"Analisi di Portafoglio Prodotto ({selected_period})")
    col3, col4 = st.columns(2)
    with col3:
        df_top, _ = prepara_dati_top_flop(df_periodo)
        fig_top = px.bar(df_top, x='Margine Totale', y='Nome Piatto', orientation='h', title='Top 10 Prodotti per Margine Totale')
        fig_top.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending', 'showgrid': False}, xaxis={'showgrid': False})
        st.plotly_chart(fig_top, use_container_width=True)
    with col4:
        _, df_flop = prepara_dati_top_flop(df_periodo)
        fig_flop = px.bar(df_flop, x='Margine Totale', y='Nome Piatto', orientation='h', title='Flop 10 Prodotti per Margine Totale')
        fig_flop.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total descending', 'showgrid': False}, xaxis={'showgrid': False})
        st.plotly_chart(fig_flop, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Placeholder per le altre pagine
else:
    st.title(selected)
    st.info("Questa sezione è in fase di sviluppo.")
