import pandas as pd

def arricchisci_dati_base(df_input):
    """
    Prende un DataFrame grezzo e aggiunge le colonne calcolate fondamentali.
    """
    df = df_input.copy()
    
    # --- MODIFICA LE STRINGHE QUI SOTTO CON I NOMI ESATTI DEL TUO FILE EXCEL ---
    
    nome_colonna_prezzo = "PrezzoVendita"  # <-- METTI QUI IL NOME ESATTO DELLA COLONNA PREZZO
    nome_colonna_quantita = "QuantitaVenduta" # <-- METTI QUI IL NOME ESATTO DELLA COLONNA QUANTITÀ
    nome_colonna_costo = "CostoIngredienti" # <-- METTI QUI IL NOME ESATTO DELLA COLONNA COSTO
    
    df['Ricavo Totale'] = df[nome_colonna_prezzo] * df[nome_colonna_quantita]
    df['Margine Unitario'] = df[nome_colonna_prezzo] - df[nome_colonna_costo]
    df['Margine Totale'] = df['Margine Unitario'] * df[nome_colonna_quantita]
    
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
