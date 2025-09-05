import pandas as pd
import numpy as np

def arricchisci_dati_base(df, quarter_columns):
    """
    Arricchisce il DataFrame con metriche calcolate per il periodo specificato.

    Args:
        df (pd.DataFrame): Il DataFrame grezzo caricato dall'Excel.
        quarter_columns (list): Una lista di stringhe con i nomi delle colonne delle quantità
                                 da sommare per il periodo di analisi (es. ['Vendite_Q1']).

    Returns:
        pd.DataFrame: Un nuovo DataFrame arricchito con le colonne calcolate.
    """
    df_enriched = df.copy()
    df_enriched['Quantita Vendute'] = df_enriched[quarter_columns].sum(axis=1)
    df_enriched['Ricavo Totale'] = df_enriched['Prezzo Vendita'] * df_enriched['Quantita Vendute']
    df_enriched['Margine Unitario'] = df_enriched['Prezzo Vendita'] - df_enriched['Costo Primo']
    df_enriched['Margine Totale'] = df_enriched['Margine Unitario'] * df_enriched['Quantita Vendute']
    df_enriched['Marginalità Media (%)'] = np.where(
        df_enriched['Prezzo Vendita'] > 0, 
        (df_enriched['Margine Unitario'] / df_enriched['Prezzo Vendita']) * 100, 0
    )
    return df_enriched

def calcola_kpi_globali(df):
    """
    Calcola i KPI aggregati per il DataFrame fornito.

    Args:
        df (pd.DataFrame): Un DataFrame arricchito dalla funzione arricchisci_dati_base.

    Returns:
        dict: Un dizionario contenente i 4 KPI principali.
    """
    total_revenue = df['Ricavo Totale'].sum()
    total_margin = df['Margine Totale'].sum()
    total_units = df['Quantita Vendute'].sum()
    average_gross_profit = (total_margin / total_revenue * 100) if total_revenue > 0 else 0
    
    return {
        "Ricavi Totali": total_revenue,
        "Margine Totale": total_margin,
        "Unità Vendute": total_units,
        "Profitto Lordo %": average_gross_profit
    }

def prepara_dati_trimestrali_per_grafico_annuale(df):
    """
    Prepara i dati per il grafico di andamento annuale.

    Args:
        df (pd.DataFrame): Il DataFrame grezzo originale.

    Returns:
        pd.DataFrame: Un DataFrame aggregato per trimestre.
    """
    trimestri = ['Q1', 'Q2', 'Q3', 'Q4']
    dati_trend = []
    for q in trimestri:
        quantita_col = f'Vendite_{q}'
        ricavi_q = (df['Prezzo Vendita'] * df[quantita_col]).sum()
        margine_q = ((df['Prezzo Vendita'] - df['Costo Primo']) * df[quantita_col]).sum()
        profittabilita_q = (margine_q / ricavi_q * 100) if ricavi_q > 0 else 0
        dati_trend.append({
            'Trimestre': q, 'Ricavi': ricavi_q, 'Margine': margine_q,
            'Profittabilità (%)': profittabilita_q
        })
    return pd.DataFrame(dati_trend)

def prepara_dati_categorie(df):
    """
    Aggrega i dati per categoria per i grafici a torta.

    Args:
        df (pd.DataFrame): Un DataFrame arricchito.

    Returns:
        tuple: Due DataFrame, uno per i ricavi e uno per il margine per categoria.
    """
    df_cat = df.groupby('Categoria').agg(
        Ricavi=('Ricavo Totale', 'sum'),
        Margine=('Margine Totale', 'sum')
    ).reset_index()
    df_ricavi_cat = df_cat[['Categoria', 'Ricavi']].copy()
    df_margine_cat = df_cat[['Categoria', 'Margine']].copy()
    return df_ricavi_cat, df_margine_cat

def prepara_dati_top_flop(df):
    """
    Identifica i 10 migliori e i 10 peggiori prodotti per margine totale.

    Args:
        df (pd.DataFrame): Un DataFrame arricchito.

    Returns:
        tuple: Due DataFrame, uno per i Top 10 e uno per i Flop 10.
    """
    df_sorted = df.sort_values('Margine Totale', ascending=False)
    df_top_10 = df_sorted.head(10)
    df_flop_10 = df_sorted.tail(10).sort_values('Margine Totale', ascending=True)
    return df_top_10, df_flop_10

def genera_insight_kpi(kpi_attuali, kpi_precedenti):
    """
    Genera insight strategici basati sul trend dei KPI.

    Args:
        kpi_attuali (dict): Il dizionario dei KPI per il periodo corrente.
        kpi_precedenti (dict): Il dizionario dei KPI per il periodo precedente, o None.

    Returns:
        str: Una stringa formattata con un commento strategico.
    """
    if kpi_precedenti is None:
        return ""
    
    margine_attuale = kpi_attuali["Margine Totale"]
    margine_precedente = kpi_precedenti["Margine Totale"]
    
    if margine_precedente > 0:
        variazione_margine = ((margine_attuale - margine_precedente) / margine_precedente) * 100
        if variazione_margine < -5:
            return (f"⚠️ **Attenzione**: Il Margine Totale è calato del **{abs(variazione_margine):.1f}%** "
                    "rispetto al trimestre precedente. Questo potrebbe indicare un aumento dei costi o "
                    "un calo delle vendite sui prodotti più profittevoli.")
        elif variazione_margine > 5:
            return (f"📈 **Trend Positivo**: Il Margine Totale è cresciuto del **{variazione_margine:.1f}%**, "
                    "indicando un miglioramento dell'efficienza o un aumento delle vendite di prodotti ad alto margine.")
    return ""

def genera_insight_strutturali(df):
    """
    Genera insight basati sulla struttura del portafoglio annuale.

    Args:
        df (pd.DataFrame): Un DataFrame arricchito che copre l'intero anno.

    Returns:
        list: Una lista di stringhe, ognuna contenente un insight strategico.
    """
    insights = []
    margine_totale = df['Margine Totale'].sum()
    if margine_totale > 0:
        top_20_percent_count = int(len(df) * 0.2)
        margine_top_20 = df.sort_values('Margine Totale', ascending=False).head(top_20_percent_count)['Margine Totale'].sum()
        
        if (margine_top_20 / margine_totale) > 0.8:
            insights.append(
                f"🎯 **Principio di Pareto Confermato**: L'analisi evidenzia che il **20%** dei prodotti "
                f"genera oltre l'**{(margine_top_20/margine_totale)*100:.0f}%** del margine totale. "
                "Questo nucleo di prodotti 'campioni' è l'asset strategico principale."
            )
    return insights