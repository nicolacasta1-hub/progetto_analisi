import pandas as pd
import numpy as np

def calcola_metriche_derivate(df_input, quantita_col):
    """
    Calcola le metriche di base per ogni prodotto (riga) del DataFrame.
    Prende in input un DataFrame e il nome della colonna delle quantità da usare.
    Restituisce un nuovo DataFrame con le colonne calcolate.
    """
    df = df_input.copy()
    
    # Standardizza il nome della colonna delle quantità per coerenza
    df.rename(columns={quantita_col: 'Quantita Venduta'}, inplace=True)
    
    # Calcoli per riga
    df['Ricavo Totale'] = df['Prezzo Vendita'] * df['Quantita Venduta']
    df['Margine Unitario'] = df['Prezzo Vendita'] - df['Costo Primo']
    df['Margine Totale'] = df['Margine Unitario'] * df['Quantita Venduta']
    
    # Calcolo della marginalità media, con gestione della divisione per zero
    df['Marginalità Media (%)'] = np.where(df['Prezzo Vendita'] > 0, (df['Margine Unitario'] / df['Prezzo Vendita']) * 100, 0)
    
    return df

def calcola_kpi_globali(df_arricchito):
    """
    Calcola i KPI aggregati per il DataFrame fornito.
    Restituisce un dizionario contenente i 4 KPI principali.
    """
    total_revenue = df_arricchito['Ricavo Totale'].sum()
    total_margin = df_arricchito['Margine Totale'].sum()
    total_units = df_arricchito['Quantita Venduta'].sum()
    
    # Calcolo del profitto lordo medio ponderato sul totale
    average_gross_profit = (total_margin / total_revenue * 100) if total_revenue > 0 else 0
    
    kpis = {
        "Ricavi Totali": total_revenue,
        "Margine di Contribuzione Totale": total_margin,
        "Piatti Venduti": total_units,
        "Profitto Lordo Medio (%)": average_gross_profit
    }
    return kpis

def prepara_dati_trimestrali_per_grafico_annuale(df_originale):
    """
    Prepara i dati per il grafico di andamento annuale, calcolando
    ricavi e margini per ogni trimestre.
    Restituisce un DataFrame specifico per questo grafico.
    """
    trimestri = ['Q1', 'Q2', 'Q3', 'Q4']
    dati_trend = []
    for q in trimestri:
        quantita_col = f'Vendite_{q}'
        ricavi_q = (df_originale['Prezzo Vendita'] * df_originale[quantita_col]).sum()
        margine_q = ((df_originale['Prezzo Vendita'] - df_originale['Costo Primo']) * df_originale[quantita_col]).sum()
        profittabilita_q = (margine_q / ricavi_q * 100) if ricavi_q > 0 else 0
        dati_trend.append({
            'Trimestre': q, 
            'Ricavi': ricavi_q, 
            'Margine': margine_q,
            'Profittabilità (%)': profittabilita_q
        })
    
    return pd.DataFrame(dati_trend)

def prepara_dati_categorie(df_arricchito):
    """
    Aggrega i dati per categoria.
    Restituisce due DataFrame: uno per l'incidenza sui ricavi e uno per l'incidenza sul margine.
    """
    # Calcolo aggregati per categoria
    df_cat = df_arricchito.groupby('Categoria').agg(
        Ricavi=('Ricavo Totale', 'sum'),
        Margine=('Margine Totale', 'sum')
    ).reset_index()
    
    total_revenue = df_arricchito['Ricavo Totale'].sum()
    total_margin = df_arricchito['Margine Totale'].sum()

    # DataFrame per incidenza ricavi
    df_ricavi_cat = df_cat[['Categoria', 'Ricavi']].copy()
    df_ricavi_cat['Percentuale'] = (df_ricavi_cat['Ricavi'] / total_revenue * 100) if total_revenue > 0 else 0
    
    # DataFrame per incidenza margine
    df_margine_cat = df_cat[['Categoria', 'Margine']].copy()
    df_margine_cat['Percentuale'] = (df_margine_cat['Margine'] / total_margin * 100) if total_margin > 0 else 0

    return df_ricavi_cat.sort_values('Percentuale', ascending=False), df_margine_cat.sort_values('Percentuale', ascending=False)

def prepara_dati_top_flop(df_arricchito):
    """
    Identifica i 10 migliori e i 10 peggiori prodotti per margine totale.
    Restituisce due DataFrame.
    """
    df_sorted = df_arricchito.sort_values('Margine Totale', ascending=False)
    
    df_top_10 = df_sorted.head(10)
    df_flop_10 = df_sorted.tail(10).sort_values('Margine Totale', ascending=True)
    
    return df_top_10, df_flop_10