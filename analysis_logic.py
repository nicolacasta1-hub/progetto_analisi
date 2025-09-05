# analysis_logic.py

import pandas as pd

def arricchisci_dati_base(df_input):
    """
    Prende un DataFrame grezzo, gestisce le date e aggiunge le colonne calcolate.
    """
    df = df_input.copy()
    
    # Assicuriamoci che la colonna delle date sia nel formato corretto
    # Cambia 'Data Vendita' con il nome esatto della tua colonna di date
    if 'Data Vendita' in df.columns:
        df['Data Vendita'] = pd.to_datetime(df['Data Vendita'])
        df['Trimestre'] = df['Data Vendita'].dt.to_period('Q').astype(str)
        df['Mese'] = df['Data Vendita'].dt.to_period('M').astype(str)
    else:
        # Se non ci sono date, non possiamo fare filtri temporali
        df['Trimestre'] = 'N/D'
        df['Mese'] = 'N/D'

    # Sostituisci questi nomi con i nomi esatti delle tue colonne
    nome_colonna_prezzo = "PrezzoVendita"
    nome_colonna_quantita = "QuantitaVenduta"
    nome_colonna_costo = "CostoIngredienti"
    
    df['Ricavo Totale'] = df[nome_colonna_prezzo] * df[nome_colonna_quantita]
    df['Margine Unitario'] = df[nome_colonna_prezzo] - df[nome_colonna_costo]
    df['Margine Totale'] = df['Margine Unitario'] * df[nome_colonna_quantita]
    
    return df

def calcola_kpi_globali(df_arricchito):
    """Calcola i KPI aggregati per la dashboard."""
    ricavi_totali = df_arricchito['Ricavo Totale'].sum()
    margine_totale = df_arricchito['Margine Totale'].sum()
    quantita_totale = df_arricchito['Quantita Vendute'].sum()
    
    if ricavi_totali > 0:
        profitto_lordo_percentuale = (margine_totale / ricavi_totali) * 100
    else:
        profitto_lordo_percentuale = 0
        
    kpi = {
        "Ricavi Totali": ricavi_totali,
        "Margine di Contribuzione Totale": margine_totale,
        "Profitto Lordo Medio (%)": profitto_lordo_percentuale,
        "Unità Vendute": quantita_totale
    }
    
    return kpi

def prepara_dati_trimestrali(df_arricchito):
    """Prepara i dati aggregati per trimestre per il grafico combinato."""
    dati_trimestrali = df_arricchito.groupby('Trimestre').agg(
        Ricavi=('Ricavo Totale', 'sum'),
        Margine=('Margine Totale', 'sum')
    ).reset_index()
    
    dati_trimestrali['Profittabilità (%)'] = (dati_trimestrali['Margine'] / dati_trimestrali['Ricavi']) * 100
    return dati_trimestrali

def prepara_dati_categorie(df_arricchito):
    """Prepara i dati aggregati per categoria per i grafici a torta e a barre."""
    # Per il grafico a torta dei ricavi
    incidenza_ricavi = df_arricchito.groupby('Categoria')['Ricavo Totale'].sum().reset_index()
    
    # Per il grafico a barre della marginalità media
    df_arricchito['Marginalità Media (%)'] = (df_arricchito['Margine Unitario'] / df_arricchito['Prezzo Vendita']) * 100
    marginalita_media = df_arricchito.groupby('Categoria')['Marginalità Media (%)'].mean().reset_index()
    
    return incidenza_ricavi, marginalita_media

def prepara_dati_top_flop(df_arricchito):
    """Prepara i dati per i grafici Top/Flop 10 prodotti per margine."""
    df_ordinato = df_arricchito.sort_values(by='Margine Totale', ascending=False)
    
    top_10 = df_ordinato.head(10)
    flop_10 = df_ordinato.tail(10).sort_values(by='Margine Totale', ascending=True)
    
    return top_10, flop_10