import pandas as pd

def arricchisci_dati_base(df_input):
    """
    Prende un DataFrame grezzo e aggiunge le colonne calcolate fondamentali.
    Questo è il primo passo per ogni analisi successiva.
    """
    # Lavoriamo su una copia per sicurezza
    df = df_input.copy()
    
    # Calcoliamo le nuove colonne
    df['Ricavo Totale'] = df['PrezzoVendita'] * df['QuantitaVenduta']
    df['Margine Unitario'] = df['PrezzoVendita'] - df['Costoingredienti']
    df['Margine Totale'] = df['Margine Unitario'] * df['QuantitaVenduta']
    
    return df

def calcola_kpi_globali(df_arricchito):
    """
    Calcola i KPI aggregati per l'intera dashboard.
    Richiede un DataFrame che sia già stato arricchito.
    """
    ricavi_totali = df_arricchito['Ricavo Totale'].sum()
    margine_totale = df_arricchito['Margine Totale'].sum()
    quantita_totale = df_arricchito['QuantitaVenduta'].sum()
    
    # Calcoliamo il profitto lordo medio, gestendo il caso di ricavi a zero
    if ricavi_totali > 0:
        profitto_lordo_percentuale = (margine_totale / ricavi_totali) * 100
    else:
        profitto_lordo_percentuale = 0
        
    # Creiamo un dizionario per restituire i risultati in modo ordinato
    kpi = {
        "Ricavi Totali": ricavi_totali,
        "Margine di Contribuzione Totale": margine_totale,
        "Profitto Lordo Medio (%)": profitto_lordo_percentuale,
        "Unità Vendute": quantita_totale
    }
    
    return kpi
