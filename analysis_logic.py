# analysis_logic.py

import pandas as pd
from typing import List, Dict, Tuple

def arricchisci_dati_base(df_input: pd.DataFrame, quarter_columns: List[str]) -> pd.DataFrame:
    """
    Takes a DataFrame and a list of quarter column names, then returns an 
    enriched DataFrame with calculated metrics.

    Args:
        df_input (pd.DataFrame): The raw DataFrame from the uploaded file.
        quarter_columns (List[str]): A list of the quarter columns to sum for calculations 
                                     (e.g., ['Vendite_Q1'] or ['Vendite_Q1', 'Vendite_Q2', ...]).

    Returns:
        pd.DataFrame: The DataFrame enriched with new calculated columns.
    """
    df = df_input.copy()
    
    # Define column names based on the provided data structure
    nome_piatto_col = "Nome Piatto"
    categoria_col = "Categoria"
    costo_primo_col = "Costo Primo"
    prezzo_vendita_col = "Prezzo Vendita"

    # Calculate total quantity sold for the selected period
    df['Quantita Vendute'] = df[quarter_columns].sum(axis=1)

    # Calculate core financial metrics
    df['Ricavo Totale'] = df[prezzo_vendita_col] * df['Quantita Vendute']
    df['Margine Unitario'] = df[prezzo_vendita_col] - df[costo_primo_col]
    df['Margine Totale'] = df['Margine Unitario'] * df['Quantita Vendute']
    
    # Calculate average margin percentage, handling division by zero
    df['Marginalità Media (%)'] = 0.0
    df.loc[df[prezzo_vendita_col] > 0, 'Marginalità Media (%)'] = \
        (df['Margine Unitario'] / df[prezzo_vendita_col]) * 100
    
    return df

def calcola_kpi_globali(df_arricchito: pd.DataFrame) -> Dict[str, float]:
    """
    Calculates the global KPIs for the dashboard.

    Args:
        df_arricchito (pd.DataFrame): The enriched DataFrame.

    Returns:
        Dict[str, float]: A dictionary containing the four main KPIs.
    """
    ricavi_totali = df_arricchito['Ricavo Totale'].sum()
    margine_totale = df_arricchito['Margine Totale'].sum()
    quantita_totale = df_arricchito['Quantita Vendute'].sum()
    
    if ricavi_totali > 0:
        profitto_lordo_percentuale = (margine_totale / ricavi_totali) * 100
    else:
        profitto_lordo_percentuale = 0.0
        
    kpi_dict = {
        "Ricavi Totali": ricavi_totali,
        "Margine di Contribuzione Totale": margine_totale,
        "Profitto Lordo Medio (%)": profitto_lordo_percentuale,
        "Unità Vendute": quantita_totale
    }
    
    return kpi_dict

def prepara_dati_trimestrali_annuali(df_originale: pd.DataFrame) -> pd.DataFrame:
    """
    Prepares data for the annual trend chart using the pre-aggregated columns.

    Args:
        df_originale (pd.DataFrame): The original, unprocessed DataFrame.

    Returns:
        pd.DataFrame: A DataFrame aggregated by quarter.
    """
    df = df_originale.copy()
    df['Margine Unitario'] = df['Prezzo Vendita'] - df['Costo Primo']
    
    ricavi_q1 = (df['Prezzo Vendita'] * df['Vendite_Q1']).sum()
    ricavi_q2 = (df['Prezzo Vendita'] * df['Vendite_Q2']).sum()
    ricavi_q3 = (df['Prezzo Vendita'] * df['Vendite_Q3']).sum()
    ricavi_q4 = (df['Prezzo Vendita'] * df['Vendite_Q4']).sum()

    margine_q1 = (df['Margine Unitario'] * df['Vendite_Q1']).sum()
    margine_q2 = (df['Margine Unitario'] * df['Vendite_Q2']).sum()
    margine_q3 = (df['Margine Unitario'] * df['Vendite_Q3']).sum()
    margine_q4 = (df['Margine Unitario'] * df['Vendite_Q4']).sum()

    dati = {
        'Trimestre': ['Q1', 'Q2', 'Q3', 'Q4'],
        'Ricavi': [ricavi_q1, ricavi_q2, ricavi_q3, ricavi_q4],
        'Margine': [margine_q1, margine_q2, margine_q3, margine_q4]
    }
    df_trimestri = pd.DataFrame(dati)
    
    df_trimestri.loc[df_trimestri['Ricavi'] > 0, 'Profittabilità (%)'] = \
        (df_trimestri['Margine'] / df_trimestri['Ricavi']) * 100
    df_trimestri['Profittabilità (%)'] = df_trimestri['Profittabilità (%)'].fillna(0)
    
    return df_trimestri

def prepara_dati_categorie(df_arricchito: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Prepares data for category analysis charts.

    Args:
        df_arricchito (pd.DataFrame): The enriched DataFrame.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple of two DataFrames for revenue 
                                           contribution and margin contribution.
    """
    incidenza_ricavi = df_arricchito.groupby('Categoria')['Ricavo Totale'].sum().reset_index()
    incidenza_margine = df_arricchito.groupby('Categoria')['Margine Totale'].sum().reset_index()
    return incidenza_ricavi, incidenza_margine

def prepara_dati_top_flop(df_arricchito: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Prepares data for Top 10 and Flop 10 product charts by margin.

    Args:
        df_arricchito (pd.DataFrame): The enriched DataFrame.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple of two DataFrames for Top 10 and Flop 10 products.
    """
    df_ordinato = df_arricchito.sort_values(by='Margine Totale', ascending=False)
    top_10 = df_ordinato.head(10)
    flop_10 = df_ordinato.tail(10).sort_values(by='Margine Totale', ascending=True)
    return top_10, flop_10

def prepara_dati_trend_prodotto(df_originale: pd.DataFrame, nome_prodotto: str) -> pd.DataFrame:
    """
    Prepares data for a single product's quarterly sales trend.

    Args:
        df_originale (pd.DataFrame): The original, unprocessed DataFrame.
        nome_prodotto (str): The name of the product to analyze.

    Returns:
        pd.DataFrame: A DataFrame with quarterly sales for the selected product.
    """
    dati_prodotto = df_originale[df_originale['Nome Piatto'] == nome_prodotto]
    if dati_prodotto.empty:
        return pd.DataFrame({'Trimestre': [], 'Quantita Vendute': []})
        
    vendite = dati_prodotto[['Vendite_Q1', 'Vendite_Q2', 'Vendite_Q3', 'Vendite_Q4']].iloc[0]
    df_trend = pd.DataFrame({
        'Trimestre': ['Q1', 'Q2', 'Q3', 'Q4'],
        'Quantita Vendute': vendite.values
    })
    return df_trend