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

    st.title("Global Dashboard 📈")
    uploaded_file = st.file_uploader(
        "Scegli un file Excel per iniziare", 
        type="xlsx"
    )
    
    if uploaded_file is not None:
        raw_df = load_data(uploaded_file)
        
        # --- SELETTORE PERIODO ---
        periodo_selezionato = st.selectbox(
            "Seleziona Periodo di Analisi",
            options=['Anno Intero', 'Q1', 'Q2', 'Q3', 'Q4']
        )

        # --- LOGICA DI CALCOLO DINAMICA E CORRETTA ---
        kpi_precedenti = None
        df_corrente = None

        if periodo_selezionato == 'Anno Intero':
            cols_correnti = ['Vendite_Q1', 'Vendite_Q2', 'Vendite_Q3', 'Vendite_Q4']
            df_corrente = arricchisci_dati_base(raw_df, cols_correnti)
        else: # Se è stato selezionato un trimestre
            q_corrente = f'Vendite_{periodo_selezionato}'
            df_corrente = arricchisci_dati_base(raw_df, [q_corrente])
            
            q_num = int(periodo_selezionato[1])
            if q_num > 1: # Se non è il Q1, calcoliamo il periodo precedente
                q_precedente = f'Vendite_Q{q_num - 1}'
                df_precedente = arricchisci_dati_base(raw_df, [q_precedente])
                kpi_precedenti = calcola_kpi_globali(df_precedente)

        # Calcoliamo i KPI per il periodo corrente
        kpi_correnti = calcola_kpi_globali(df_corrente)
        
        st.divider()

        # --- KPI CARDS CON TREND DINAMICO ---
        st.header("KPI Globali")
        col1, col2, col3, col4 = st.columns(4)

        # Calcoliamo il delta (variazione) solo se kpi_precedenti esiste
        delta_ricavi = None
        if kpi_precedenti:
            delta_ricavi = (kpi_correnti['Ricavi Totali'] - kpi_precedenti['Ricavi Totali']) / kpi_precedenti['Ricavi Totali']
        
        with col1: 
            st.metric(
                label="Ricavi Totali", 
                value=f"€ {kpi_correnti['Ricavi Totali']:.2f}",
                delta=f"{delta_ricavi:.1%}" if delta_ricavi is not None else None
            )
        
        # (Puoi fare lo stesso per gli altri KPI se vuoi mostrare anche il loro trend)
        with col2: st.metric(label="Margine Totale", value=f"€ {kpi_correnti['Margine di Contribuzione Totale']:.2f}")
        with col3: st.metric(label="Profitto Lordo Medio", value=f"{kpi_correnti['Profitto Lordo Medio (%)']:.1f} %")
        with col4: st.metric(label="Unità Vendute", value=f"{kpi_correnti['Unità Vendute']}")
        
        st.divider()

        # --- INSIGHTS STRATEGICI AUTOMATICI ---
        st.header("🔍 Insight Strategici Automatici")
        
        # Ora la chiamata alla funzione è corretta!
        insight_trend_list = analizza_kpi_trends(kpi_correnti, kpi_precedenti)
        if insight_trend_list:
            st.info(insight_trend_list[0])

        # Le analisi strutturali usano sempre i dati annuali completi
        df_annuale = arricchisci_dati_base(raw_df, ['Vendite_Q1', 'Vendite_Q2', 'Vendite_Q3', 'Vendite_Q4'])
        insight_strutturali_list = analizza_struttura_business(df_annuale)
        for insight in insight_strutturali_list:
            st.info(insight)
        
        st.divider()
    
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
