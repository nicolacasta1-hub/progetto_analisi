import pandas as pd

def analizza_kpi_trends(kpi_attuali, kpi_precedenti):
    """
    Genera un insight basato sul trend di un KPI rispetto al periodo precedente.

    Args:
        kpi_attuali (dict): Dizionario dei KPI per il periodo corrente.
        kpi_precedenti (dict): Dizionario dei KPI per il periodo precedente, o None.

    Returns:
        list: Una lista contenente (o vuota) una stringa con l'insight strategico.
    """
    if kpi_precedenti is None:
        return []

    insights = []
    
    # Estrazione dei valori con controllo di esistenza
    margine_attuale = kpi_attuali.get("Margine di Contribuzione Totale", 0)
    margine_precedente = kpi_precedenti.get("Margine di Contribuzione Totale", 0)
    
    # Calcolo della variazione solo se il dato precedente è valido
    if margine_precedente > 0:
        variazione_perc = ((margine_attuale - margine_precedente) / margine_precedente) * 100
        
        # Trigger: Se il margine è calato di più del 5%
        if variazione_perc < -5:
            insight = (
                f"⚠️ **Tendenza Negativa:** Il Margine Totale è calato del {abs(variazione_perc):.1f}% rispetto al trimestre precedente. "
                "**Implicazione:** La profittabilità sta diminuendo. "
                "**Raccomandazione:** Investigare se la causa è un calo dei volumi di vendita o un aumento dei costi delle materie prime."
            )
            insights.append(insight)
            
    return insights

def analizza_struttura_business(df_annuale):
    """
    Analizza la struttura complessiva del business basandosi sui dati annuali.

    Args:
        df_annuale (pd.DataFrame): DataFrame arricchito con i dati dell'intero anno.

    Returns:
        list: Una lista di stringhe, ognuna contenente un insight strutturale.
    """
    insights = []
    
    # Assicuriamoci che il dataframe non sia vuoto per evitare errori
    if df_annuale.empty:
        return []
        
    margine_totale_complessivo = df_annuale['Margine Totale'].sum()
    
    # Se non c'è margine, non ha senso fare analisi
    if margine_totale_complessivo <= 0:
        return []

    # --- a) Analisi di Pareto (80/20 Rule) ---
    top_20_percent_count = int(len(df_annuale) * 0.2)
    if top_20_percent_count > 0:
        df_sorted = df_annuale.sort_values('Margine Totale', ascending=False)
        margine_top_20 = df_sorted.head(top_20_percent_count)['Margine Totale'].sum()
        perc_margine_top_20 = (margine_top_20 / margine_totale_complessivo) * 100
        
        # Trigger: Se il top 20% dei prodotti genera più dell'80% del margine
        if perc_margine_top_20 > 80:
            insight = (
                "**Insight - Principio di Pareto Rispettato:**\n\n"
                f"* **Osservazione:** L'analisi mostra che l'{perc_margine_top_20:.0f}% del margine totale è generato solo dal 20% dei prodotti a menu.\n"
                "* **Implicazione:** Il business ha un nucleo di prodotti 'campioni' estremamente forte, ma anche una forte dipendenza da essi.\n"
                "* **Raccomandazione:** Proteggere questi prodotti chiave (qualità, disponibilità) è la priorità assoluta. Utilizzarli come leva di marketing per attirare i clienti."
            )
            insights.append(insight)

    # --- b) Analisi della "Coda Lunga" (Long-Tail Analysis) ---
    bottom_50_percent_count = int(len(df_annuale) * 0.5)
    if bottom_50_percent_count > 0:
        df_sorted_asc = df_annuale.sort_values('Margine Totale', ascending=True)
        margine_bottom_50 = df_sorted_asc.head(bottom_50_percent_count)['Margine Totale'].sum()
        perc_margine_coda = (margine_bottom_50 / margine_totale_complessivo) * 100
        
        # Trigger: Se il 50% meno performante dei prodotti genera meno del 5% del margine
        if perc_margine_coda < 5:
            insight = (
                "**Insight - Presenza di una 'Coda Lunga' Improduttiva:**\n\n"
                f"* **Osservazione:** La metà meno performante dei prodotti (il 50%) genera complessivamente meno del {perc_margine_coda:.0f}% del margine totale.\n"
                "* **Implicazione:** Molti prodotti a menu stanno complicando le operazioni in cucina e i costi di magazzino, senza contribuire in modo significativo alla profittabilità.\n"
                "* **Raccomandazione:** Valutare uno snellimento del menu. Considerare l'eliminazione dei prodotti meno performanti per ridurre la complessità e focalizzare l'attenzione dei clienti sull'offerta più redditizia."
            )
            insights.append(insight)

    # --- c) Analisi Sbilanciamento Categorie (Workhorse Categories) ---
    ricavo_totale_complessivo = df_annuale['Ricavo Totale'].sum()
    df_cat = df_annuale.groupby('Categoria').agg(
        Ricavi=('Ricavo Totale', 'sum'),
        Margine=('Margine Totale', 'sum')
    ).reset_index()

    df_cat['% Contribuzione Ricavi'] = (df_cat['Ricavi'] / ricavo_totale_complessivo) * 100
    df_cat['% Contribuzione Margine'] = (df_cat['Margine'] / margine_totale_complessivo) * 100
    
    # Trigger: Se la contribuzione ai ricavi è maggiore di quella ai margini di 10 punti
    for _, row in df_cat.iterrows():
        if (row['% Contribuzione Ricavi'] - row['% Contribuzione Margine']) > 10:
            insight = (
                "**Insight - Categoria 'Cavallo di Battaglia' Identificata:**\n\n"
                f"* **Osservazione:** La categoria '{row['Categoria']}' genera il {row['% Contribuzione Ricavi']:.0f}% dei ricavi, ma solo il {row['% Contribuzione Margine']:.0f}% dei margini.\n"
                "* **Implicazione:** Questa categoria è molto popolare e attira clienti, ma la sua bassa profittabilità sta 'diluendo' il margine complessivo dell'azienda.\n"
                "* **Raccomandazione:** Avviare un'iniziativa di ottimizzazione su questa categoria: analizzare i costi primi dei prodotti più venduti al suo interno e/o testare lievi aumenti di prezzo."
            )
            insights.append(insight)

    return insights