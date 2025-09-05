import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from analysis_logic import (
    calcola_metriche_derivate,
    calcola_kpi_globali,
    prepara_dati_trimestrali_per_grafico_annuale,
    prepara_dati_categorie,
    prepara_dati_top_flop
)

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(
    page_title="Decision Intelligence Dashboard",
    page_icon="💼",
    layout="wide"
)

# --- CARICAMENTO CSS ---
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
local_css("style.css")

# --- SIDEBAR ---
with st.sidebar:
    st.title("💼 Dashboard di Analisi")
    st.info(
        "Questo strumento è progettato per trasformare i dati di vendita in "
        "insight strategici e supportare le decisioni aziendali."
    )
    st.warning("Assicurarsi che il file Excel caricato contenga le colonne: 'Nome Piatto', 'Categoria', 'Costo Primo', 'Prezzo Vendita', e 'Vendite_Q1' a 'Vendite_Q4'.")

# --- PAGINA PRINCIPALE ---
st.title("Dashboard Globale di Analisi Decisionale")

uploaded_file = st.file_uploader("Carica qui il tuo file di analisi (formato .xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        raw_df = pd.read_excel(uploaded_file)
    except Exception as e:
        st.error(f"Errore nella lettura del file Excel: {e}")
        st.stop()

    # --- SELETTORE DEL PERIODO (FEATURE CHIAVE) ---
    selected_period = st.selectbox(
        "Seleziona Periodo di Analisi",
        options=['Anno Intero', 'Q1', 'Q2', 'Q3', 'Q4'],
        index=0 # 'Anno Intero' di default
    )

    # --- LOGICA DI FILTRAGGIO DINAMICO DEI DATI ---
    if selected_period == 'Anno Intero':
        # Creiamo una colonna temporanea per le vendite annuali
        raw_df['Quantita Totale'] = raw_df[['Vendite_Q1', 'Vendite_Q2', 'Vendite_Q3', 'Vendite_Q4']].sum(axis=1)
        quantita_col_da_usare = 'Quantita Totale'
    else: # Se è selezionato un trimestre
        quantita_col_da_usare = f'Vendite_{selected_period}'
    
    # Calcoliamo le metriche derivate per il periodo selezionato
    df_periodo = calcola_metriche_derivate(raw_df, quantita_col_da_usare)

    # --- SEZIONE KPI ---
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("Indicatori di Performance Chiave (KPIs)")
    
    kpis = calcola_kpi_globali(df_periodo)
    
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    
    with kpi1:
        st.markdown(f'<div class="kpi-card"><h4>Ricavi Totali</h4><p>€ {kpis["Ricavi Totali"]:,.2f}</p></div>', unsafe_allow_html=True)
    with kpi2:
        st.markdown(f'<div class="kpi-card"><h4>Margine di Contribuzione Totale</h4><p>€ {kpis["Margine di Contribuzione Totale"]:,.2f}</p></div>', unsafe_allow_html=True)
    with kpi3:
        st.markdown(f'<div class="kpi-card"><h4>Piatti Venduti</h4><p>{int(kpis["Piatti Venduti"])}</p></div>', unsafe_allow_html=True)
    with kpi4:
        st.markdown(f'<div class="kpi-card"><h4>Profitto Lordo Medio %</h4><p>{kpis["Profitto Lordo Medio (%)"]:.2f}%</p></div>', unsafe_allow_html=True)

    # --- GRAFICI ---
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # --- GRAFICO CONDIZIONALE: ANDAMENTO ANNUALE ---
    if selected_period == 'Anno Intero':
        st.subheader("Andamento Performance Annuale")
        df_trend = prepara_dati_trimestrali_per_grafico_annuale(raw_df)
        
        # Creazione del grafico combinato con Plotly
        fig_trend = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Barra per Ricavi
        fig_trend.add_trace(go.Bar(
            x=df_trend['Trimestre'], 
            y=df_trend['Ricavi'], 
            name='Ricavi (€)',
            marker_color='#7792E3'
        ), secondary_y=False)
        
        # Linea per Profittabilità
        fig_trend.add_trace(go.Scatter(
            x=df_trend['Trimestre'], 
            y=df_trend['Profittabilità (%)'], 
            name='Profittabilità (%)', 
            mode='lines+markers',
            marker_color='#34A853'
        ), secondary_y=True)

        fig_trend.update_layout(
            title_text='Ricavi vs. Profittabilità per Trimestre',
            template='plotly_dark',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        fig_trend.update_yaxes(title_text="Ricavi (€)", secondary_y=False)
        fig_trend.update_yaxes(title_text="Profittabilità (%)", secondary_y=True)
        
        st.plotly_chart(fig_trend, use_container_width=True)

    # --- ALTRI GRAFICI (SEMPRE VISIBILI) ---
    st.subheader("Analisi dei Driver di Performance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        df_ricavi_cat, df_margine_cat = prepara_dati_categorie(df_periodo)
        
        fig_ric_cat = px.bar(df_ricavi_cat, x='Percentuale', y='Categoria', orientation='h', title='Ripartizione Ricavi per Categoria (%)')
        fig_ric_cat.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_ric_cat, use_container_width=True)

    with col2:
        df_ricavi_cat, df_margine_cat = prepara_dati_categorie(df_periodo) # Ricalcolo per sicurezza
        
        fig_mar_cat = px.bar(df_margine_cat, x='Percentuale', y='Categoria', orientation='h', title='Ripartizione Margine per Categoria (%)')
        fig_mar_cat.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_mar_cat, use_container_width=True)

    st.subheader("Analisi di Portafoglio Prodotto")

    col3, col4 = st.columns(2)
    
    with col3:
        df_top, df_flop = prepara_dati_top_flop(df_periodo)
        
        fig_top = px.bar(df_top, x='Margine Totale', y='Nome Piatto', orientation='h', title='Top 10 Prodotti per Margine Totale')
        fig_top.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_top, use_container_width=True)

    with col4:
        df_top, df_flop = prepara_dati_top_flop(df_periodo) # Ricalcolo per sicurezza
        
        fig_flop = px.bar(df_flop, x='Margine Totale', y='Nome Piatto', orientation='h', title='Flop 10 Prodotti per Margine Totale')
        fig_flop.update_layout(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', yaxis={'categoryorder':'total descending'})
        st.plotly_chart(fig_flop, use_container_width=True)

else:
    st.info("In attesa di un file Excel per avviare l'analisi.")