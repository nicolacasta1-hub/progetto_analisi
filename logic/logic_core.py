# logic/logic_core.py

import pandas as pd
from typing import Dict, List, Tuple

def arricchisci_dati_base(df_input: pd.DataFrame) -> pd.DataFrame:
    """Prende il DataFrame grezzo e aggiunge le colonne calcolate annuali."""
    df = df_input.copy()
    col_prezzo = "Prezzo Vendita"
    col_costo = "Costo Primo"
    col_q1 = "Vendite_Q1"
    col_q2 = "Vendite_Q2"
    col_q3 = "Vendite_Q3"
    col_q4 = "Vendite_Q4"

    df['Quantita Totale Anno'] = df[[col_q1, col_q2, col_q3, col_q4]].sum(axis=1)
    df['Ricavo Totale'] = df[col_prezzo] * df['Quantita Totale Anno']
    df['Margine Unitario'] = df[col_prezzo] - df[col_costo]
    df['Margine Totale'] = df['Margine Unitario'] * df['Quantita Totale Anno']
    
    df['Marginalità (%)'] = 0.0
    df.loc[df[col_prezzo] > 0, 'Marginalità (%)'] = \
        (df['Margine Unitario'] / df[col_prezzo]) * 100
    
    return df

def processa_dati_per_periodo(df_input: pd.DataFrame, periodo: str) -> pd.DataFrame:
    """
    Prende il DF originale e lo elabora per un periodo specifico ('Q1', 'Anno Intero', etc.).
    Questa funzione è il cuore del filtro della dashboard.
    """
    df = df_input.copy()

    if periodo == 'Anno Intero':
        colonne_quantita = ['Vendite_Q1', 'Vendite_Q2', 'Vendite_Q3', 'Vendite_Q4']
    else:
        colonne_quantita = [f'Vendite_{periodo}']

    df['Quantita Periodo'] = df[colonne_quantita].sum(axis=1)
    
    df['Ricavo Periodo'] = df['Prezzo Vendita'] * df['Quantita Periodo']
    df['Margine Unitario'] = df['Prezzo Vendita'] - df['Costo Primo']
    df['Margine Periodo'] = df['Margine Unitario'] * df['Quantita Periodo']
    
    return df

def calcola_kpi(df_periodo: pd.DataFrame) -> Dict[str, float]:
    """Calcola i KPI sul DataFrame di un periodo specifico."""
    ricavi = df_periodo['Ricavo Periodo'].sum()
    margine = df_periodo['Margine Periodo'].sum()
    quantita = df_periodo['Quantita Periodo'].sum()

    if ricavi > 0:
        profitto_lordo_perc = (margine / ricavi) * 100
    else:
        profitto_lordo_perc = 0.0

    return {
        "Ricavi Totali": ricavi,
        "Margine di Contribuzione Totale": margine,
        "Profitto Lordo Medio (%)": profitto_lordo_perc,
        "Unità Vendute": quantita
    }

def prepara_dati_trimestrali_annuali(df_originale: pd.DataFrame) -> pd.DataFrame:
    """Prepara i dati per il grafico di andamento annuale."""
    # (Questa funzione richiede una logica simile a quella del test, la implementiamo per completezza)
    df = df_originale.copy()
    df['Margine Unitario'] = df['Prezzo Vendita'] - df['Costo Primo']
    
    ricavi_q = [(df['Prezzo Vendita'] * df[f'Vendite_Q{i}']).sum() for i in range(1, 5)]
    margine_q = [(df['Margine Unitario'] * df[f'Vendite_Q{i}']).sum() for i in range(1, 5)]

    dati = {'Trimestre': ['Q1', 'Q2', 'Q3', 'Q4'], 'Ricavi': ricavi_q, 'Margine': margine_q}
    df_trimestri = pd.DataFrame(dati)
    
    df_trimestri.loc[df_trimestri['Ricavi'] > 0, 'Profittabilità (%)'] = \
        (df_trimestri['Margine'] / df_trimestri['Ricavi']) * 100
    df_trimestri['Profittabilità (%)'] = df_trimestri['Profittabilità (%)'].fillna(0)
    
    return df_trimestri

def prepara_dati_categorie(df_periodo: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Prepara i dati aggregati per categoria per il periodo selezionato."""
    incidenza_ricavi = df_periodo.groupby('Categoria')['Ricavo Periodo'].sum().reset_index()
    incidenza_margine = df_periodo.groupby('Categoria')['Margine Periodo'].sum().reset_index()
    return incidenza_ricavi, incidenza_margine

def prepara_dati_top_flop(df_periodo: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Prepara i dati per i grafici Top/Flop 10 per il periodo selezionato."""
    df_ordinato = df_periodo.sort_values(by='Margine Periodo', ascending=False)
    top_10 = df_ordinato.head(10)
    flop_10 = df_ordinato.tail(10).sort_values(by='Margine Periodo', ascending=True)
    return top_10, flop_10

def calcola_break_even_point(costi_fissi: float, df_periodo: pd.DataFrame) -> dict:
    """
    Calcola il Break-Even Point (BEP) in termini di fatturato e unità per il periodo dato.
    """
    ricavi_totali = df_periodo['Ricavo Periodo'].sum()
    margine_totale = df_periodo['Margine Periodo'].sum()
    quantita_totale = df_periodo['Quantita Periodo'].sum()

    margine_di_contribuzione_ratio = (margine_totale / ricavi_totali) if ricavi_totali != 0 else 0.0
    bep_fatturato = (costi_fissi / margine_di_contribuzione_ratio) if margine_di_contribuzione_ratio != 0 else 0.0

    margine_medio_unitario = (margine_totale / quantita_totale) if quantita_totale != 0 else 0.0
    bep_unita = (costi_fissi / margine_medio_unitario) if margine_medio_unitario != 0 else 0.0

    return {
        'ricavi_totali': ricavi_totali,
        'margine_totale': margine_totale,
        'quantita_totale': quantita_totale,
        'margine_di_contribuzione_ratio': margine_di_contribuzione_ratio,
        'bep_fatturato': bep_fatturato,
        'margine_medio_unitario': margine_medio_unitario,
        'bep_unita': bep_unita,
        'costi_fissi': costi_fissi
    }

def prepara_dati_grafico_bep(costi_fissi: float, df_periodo: pd.DataFrame) -> pd.DataFrame:
    """
    Prepara i dati per il grafico del Break-Even Point (BEP).
    """
    ricavi_totali = df_periodo['Ricavo Periodo'].sum()
    margine_totale = df_periodo['Margine Periodo'].sum()
    quantita_totale = df_periodo['Quantita Periodo'].sum()

    if quantita_totale != 0:
        costo_variabile_unitario_medio = (ricavi_totali - margine_totale) / quantita_totale
        prezzo_unitario_medio = ricavi_totali / quantita_totale
    else:
        costo_variabile_unitario_medio = 0.0
        prezzo_unitario_medio = 0.0

    max_volume = int(quantita_totale * 1.5) if quantita_totale > 0 else 100
    volumi = list(range(0, max_volume + 1, max(1, max_volume // 100)))

    dati = {
        'Unità Vendute': [],
        'Ricavi Totali': [],
        'Costi Fissi': [],
        'Costi Totali': []
    }

    for v in volumi:
        ricavi = prezzo_unitario_medio * v
        costi_variabili = costo_variabile_unitario_medio * v
        costi_totali = costi_fissi + costi_variabili
        dati['Unità Vendute'].append(v)
        dati['Ricavi Totali'].append(ricavi)
        dati['Costi Fissi'].append(costi_fissi)
        dati['Costi Totali'].append(costi_totali)

    return pd.DataFrame(dati)