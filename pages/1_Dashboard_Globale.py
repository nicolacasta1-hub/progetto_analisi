# pages/1_Dashboard_Globale.py

import streamlit as st
import pandas as pd
import plotly.express as px
from utils import local_css

# Importiamo le funzioni di logica necessarie
from logic.logic_core import (
    processa_dati_per_periodo,
    calcola_kpi,
    prepara_dati_trimestrali_annuali,
    prepara_dati_categorie,
    prepara_dati_top_flop,
    calcola_break_even_point,
    prepara_dati_grafico_bep
)
# --- IMPOSTAZIONI SPECIFICHE DELLA PAGINA ---
st.set_page_config(
    layout="wide", 
    page_title="Dashboard Globale",
    initial_sidebar_state="expanded"
)
local_css("style.css")
st.title("Global Dashboard 📈")

# --- DATA GUARD: Controlliamo se i dati sono stati caricati ---
if st.session_state.get('df') is None:
    st.warning("Per favore, carica un file di dati nella pagina 'Caricamento Dati' per iniziare.")
    st.stop() # Interrompe l'esecuzione se non ci sono dati

# Se siamo qui, significa che i dati esistono
df_annuale = st.session_state['df']

# --- SELETTORE PERIODO ---
periodo_selezionato = st.selectbox(
    "Seleziona Periodo di Analisi",
    options=['Anno Intero', 'Q1', 'Q2', 'Q3', 'Q4']
)

# --- CALCOLO DINAMICO DEI DATI PER IL PERIODO SELEZIONATO ---
df_periodo = processa_dati_per_periodo(df_annuale, periodo_selezionato)
kpi_correnti_dict = calcola_kpi(df_periodo)

# --- Calcolo Break-Even Point ---
# Assicuriamoci che l'utente abbia inserito i costi fissi
if 'costi_fissi' in st.session_state and st.session_state['costi_fissi'] > 0:
    bep_dict = calcola_break_even_point(st.session_state['costi_fissi'], df_periodo)
    bep_fatturato = bep_dict.get('bep_fatturato', 0)
else:
    bep_fatturato = 0 # Se non ci sono costi fissi, il BEP è zero

# Calcolo KPI per trend (periodo precedente)
kpi_precedenti_dict = None
q_num = int(periodo_selezionato[1]) if periodo_selezionato.startswith('Q') else 0
if q_num > 1:
    df_precedente = processa_dati_per_periodo(df_annuale, f'Q{q_num - 1}')
    kpi_precedenti_dict = calcola_kpi(df_precedente)

# --- VISUALIZZAZIONE KPI CARDS ---
st.divider()
st.header("KPI Globali")
kpi_cols = st.columns(5)

# Helper function to calculate delta
def calc_delta(current, previous):
    if kpi_precedenti_dict and previous != 0:
        return (current - previous) / previous
    return None

# Ricavi Totali
ricavi_corr = kpi_correnti_dict['Ricavi Totali']
ricavi_prec = kpi_precedenti_dict['Ricavi Totali'] if kpi_precedenti_dict else None
delta_ricavi = calc_delta(ricavi_corr, ricavi_prec) if ricavi_prec is not None else None
kpi_cols[0].metric(
    label=f"Ricavi Totali ({periodo_selezionato})",
    value=f"€ {ricavi_corr:.2f}",
    delta=f"{delta_ricavi:.1%}" if delta_ricavi is not None else None
)

# Margine di Contribuzione Totale
margine_corr = kpi_correnti_dict['Margine di Contribuzione Totale']
margine_prec = kpi_precedenti_dict['Margine di Contribuzione Totale'] if kpi_precedenti_dict else None
delta_margine = calc_delta(margine_corr, margine_prec) if margine_prec is not None else None
kpi_cols[1].metric(
    label=f"Margine Totale ({periodo_selezionato})",
    value=f"€ {margine_corr:.2f}",
    delta=f"{delta_margine:.1%}" if delta_margine is not None else None
)

# Profitto Lordo Medio (%)
profitto_corr = kpi_correnti_dict['Profitto Lordo Medio (%)']
profitto_prec = kpi_precedenti_dict['Profitto Lordo Medio (%)'] if kpi_precedenti_dict else None
delta_profitto = calc_delta(profitto_corr, profitto_prec) if profitto_prec is not None else None
kpi_cols[2].metric(
    label=f"Profitto Lordo Medio ({periodo_selezionato})",
    value=f"{profitto_corr:.1f} %",
    delta=f"{delta_profitto:.1%}" if delta_profitto is not None else None
)

# Unità Vendute
unita_corr = kpi_correnti_dict['Unità Vendute']
unita_prec = kpi_precedenti_dict['Unità Vendute'] if kpi_precedenti_dict else None
delta_unita = calc_delta(unita_corr, unita_prec) if unita_prec is not None else None
kpi_cols[3].metric(
    label=f"Unità Vendute ({periodo_selezionato})",
    value=f"{unita_corr}",
    delta=f"{delta_unita:.1%}" if delta_unita is not None else None
)
 # Break-Even Point
kpi_cols[4].metric(
        label=f"Break-Even Point ({periodo_selezionato})",
        value=f"€ {bep_fatturato:,.2f}"
    )
st.divider()

# --- VISUALIZZAZIONI GRAFICHE ---

# Grafico condizionale che appare solo per 'Anno Intero'
if periodo_selezionato == 'Anno Intero':
    st.header("Andamento Performance Annuale")
    dati_chart_trimestri = prepara_dati_trimestrali_annuali(df_annuale)
    fig_trimestri = px.bar(dati_chart_trimestri, x='Trimestre', y='Ricavi')
    fig_trimestri.add_scatter(x=dati_chart_trimestri['Trimestre'], y=dati_chart_trimestri['Profittabilità (%)'], mode='lines', name='Profittabilità (%)', yaxis='y2')
    fig_trimestri.update_layout(yaxis2=dict(overlaying='y', side='right'), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    st.plotly_chart(fig_trimestri, use_container_width=True)
    st.divider()

st.header(f"Analisi di Dettaglio per: {periodo_selezionato}")

# (Il resto del codice per i grafici delle categorie e Top/Flop rimane identico a prima)
incidenza_ricavi, incidenza_margine = prepara_dati_categorie(df_periodo)
col_graf_1, col_graf_2 = st.columns(2)
with col_graf_1:
    fig_torta_ricavi = px.pie(incidenza_ricavi, names='Categoria', values='Ricavo Periodo', title='Incidenza Ricavi per Categoria', hole=0.4)
    st.plotly_chart(fig_torta_ricavi, use_container_width=True)
with col_graf_2:
    fig_torta_margine = px.pie(incidenza_margine, names='Categoria', values='Margine Periodo', title='Incidenza Margine per Categoria', hole=0.4)
    st.plotly_chart(fig_torta_margine, use_container_width=True)

st.divider()

top_10, flop_10 = prepara_dati_top_flop(df_periodo)
col_top, col_flop = st.columns(2)
with col_top:
    fig_top = px.bar(top_10, x='Margine Periodo', y='Nome Piatto', orientation='h', title='Top 10 Prodotti per Margine')
    fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top, use_container_width=True)
with col_flop:
    fig_flop = px.bar(flop_10, x='Margine Periodo', y='Nome Piatto', orientation='h', title='Flop 10 Prodotti per Margine')
    fig_flop.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_flop, use_container_width=True)

 # --- GRAFICO BREAK-EVEN POINT ---

st.divider()
st.header("Break-Even Point")

# Prepara i dati per il grafico BEP
bep_chart_data = prepara_dati_grafico_bep(st.session_state['costi_fissi'], df_periodo)
fig = px.line(
    bep_chart_data,
    x="Unità Vendute",
    y=["Ricavi Totali", "Costi Totali", "Costi Fissi"],
    labels={
        "value": "Euro (€)",
        "Unità Vendute": "Unità Vendute",
        "variable": "Voce"
    }
)

# Trova il punto di intersezione (Break-Even Point)
bep_unita = bep_dict.get('bep_unita', None)
if bep_unita is not None:
    # Linea verticale sul BEP
    fig.add_vline(
        x=bep_unita,
        line_dash="dash",
        line_color="red"
    )
    # Annotazione testuale
    fig.add_annotation(
        x=bep_unita,
        y=bep_fatturato,
        text=f"BEP: {int(bep_unita)} unità<br>€ {bep_fatturato:,.2f}",
        showarrow=True,
        arrowhead=2,
        ax=40,
        ay=-40,
        bgcolor="rgba(0,0,0,0.7)",
        font=dict(color="white")
    )

# Stile dark professionale
fig.update_layout(
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font_color='white',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    title_font=dict(size=20, color='white')
)
fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')
fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(255,255,255,0.1)')

st.plotly_chart(fig, use_container_width=True)
    