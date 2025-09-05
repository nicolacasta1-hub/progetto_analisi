import pandas as pd
import numpy as np

def arricchisci_dati_base(df, quarter_columns):
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

# All'interno del file analysis_logic.py, sostituite la vecchia funzione con questa:

def prepara_dati_categorie(df_arricchito):
    df_cat = df_arricchito.groupby('Categoria').agg(
        Ricavi=('Ricavo Totale', 'sum'),
        Margine=('Margine Totale', 'sum')
    ).reset_index()
    df_ricavi_cat = df_cat[['Categoria', 'Ricavi']].copy()
    df_margine_cat = df_cat[['Categoria', 'Margine']].copy()

    return df_ricavi_cat, df_margine_cat

def prepara_dati_top_flop(df):
    df_sorted = df.sort_values('Margine Totale', ascending=False)
    df_top_10 = df_sorted.head(10)
    df_flop_10 = df_sorted.tail(10).sort_values('Margine Totale', ascending=True)
    return df_top_10, df_flop_10

def genera_insight_kpi(kpi_attuali, kpi_precedenti):
    if kpi_precedenti is None:
        return ""
    
    insights = []
    margine_attuale = kpi_attuali["Margine Totale"]
    margine_precedente = kpi_precedenti["Margine Totale"]
    
    if margine_precedente > 0:
        variazione_margine = ((margine_attuale - margine_precedente) / margine_precedente) * 100
        if variazione_margine < -5:
            insights.append(
                f"⚠️ **Attenzione**: Il Margine Totale è calato del **{abs(variazione_margine):.1f}%** "
                "rispetto al trimestre precedente. Questo potrebbe indicare un aumento dei costi o "
                "un calo delle vendite sui prodotti più profittevoli."
            )
        elif variazione_margine > 5:
            insights.append(
                f"📈 **Trend Positivo**: Il Margine Totale è cresciuto del **{variazione_margine:.1f}%**, "
                "indicando un miglioramento dell'efficienza o un aumento delle vendite di prodotti ad alto margine."
            )

    return " ".join(insights)

def genera_insight_strutturali(df_annuale):
    insights = []
    margine_totale = df_annuale['Margine Totale'].sum()
    if margine_totale > 0:
        top_20_percent_count = int(len(df_annuale) * 0.2)
        margine_top_20 = df_annuale.sort_values('Margine Totale', ascending=False).head(top_20_percent_count)['Margine Totale'].sum()
        
        if (margine_top_20 / margine_totale) > 0.8:
            insights.append(
                f"🎯 **Principio di Pareto Confermato**: L'analisi evidenzia che il **20%** dei prodotti "
                f"genera oltre l'**{(margine_top_20/margine_totale)*100:.0f}%** del margine totale. "
                "Questo nucleo di prodotti 'campioni' è l'asset strategico principale."
            )

    df_cat = df_annuale.groupby('Categoria').agg(Ricavi=('Ricavo Totale', 'sum'), Margine=('Margine Totale', 'sum')).reset_index()
    if not df_cat.empty and df_cat['Ricavi'].sum() > 0:
        df_cat['MDC_%'] = (df_cat['Margine'] / df_cat['Ricavi']) * 100
        df_cat['Incidenza_Ricavi_%'] = (df_cat['Ricavi'] / df_cat['Ricavi'].sum()) * 100
        media_mdc = (df_cat['Margine'].sum() / df_cat['Ricavi'].sum()) * 100
        cavalli_cat = df_cat[(df_cat['Incidenza_Ricavi_%'] > 15) & (df_cat['MDC_%'] < media_mdc)]
        
        if not cavalli_cat.empty:
            nome_cat = cavalli_cat.iloc[0]['Categoria']
            insights.append(
                f"🐴 **Categoria 'Cavallo di Battaglia'**: La categoria **'{nome_cat}'** genera una quota "
                "importante di ricavi ma con una profittabilità inferiore alla media. È un'area prioritaria "
                "per interventi di ottimizzazione."
            )
    return insights