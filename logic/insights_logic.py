import pandas as pd
from typing import List, Dict, Optional

def analizza_kpi_trends(
    kpi_attuali: Dict[str, float],
    kpi_precedenti: Optional[Dict[str, float]]
) -> List[str]:
    """
    Analizza la variazione del Margine di Contribuzione Totale tra due periodi e genera insight strategici.

    Parameters:
        kpi_attuali (dict): Dizionario dei KPI del periodo attuale. Deve contenere la chiave 'Margine di Contribuzione Totale'.
        kpi_precedenti (dict | None): Dizionario dei KPI del periodo precedente, con la stessa struttura. Può essere None.

    Returns:
        list[str]: Lista di stringhe contenenti insight formattati secondo la logica OIR. Lista vuota se nessun trigger è attivato.
    """
    if kpi_precedenti is None:
        return []

    current_margin = kpi_attuali.get('Margine di Contribuzione Totale', None)
    previous_margin = kpi_precedenti.get('Margine di Contribuzione Totale', None)

    if current_margin is None or previous_margin is None:
        return []

    if previous_margin == 0:
        return []

    variazione_perc = (current_margin - previous_margin) / previous_margin

    if variazione_perc < -0.05:
        return [
            (
                "⚠️ **Tendenza Negativa Rilevata:**\n\n"
                f"* **Osservazione:** Il Margine Totale è calato del {variazione_perc:.1%} rispetto al trimestre precedente.\n"
                "* **Implicazione:** La profittabilità complessiva sta diminuendo, indicando un potenziale problema di costi o un calo nelle vendite dei prodotti più redditizi.\n"
                "* **Raccomandazione:** Si consiglia di investigare le performance dei prodotti 'Stella' in questo periodo e di verificare eventuali aumenti dei costi primi."
            )
        ]
    elif variazione_perc > 0.10:
        return [
            (
                "✅ **Tendenza Positiva Rilevata:**\n\n"
                f"* **Osservazione:** Il Margine Totale è cresciuto del {variazione_perc:.1%} rispetto al trimestre precedente.\n"
                "* **Implicazione:** Le strategie adottate stanno producendo risultati eccellenti e la profittabilità sta aumentando.\n"
                "* **Raccomandazione:** Capitalizzare su questo momentum. Analizzare quali prodotti o categorie hanno trainato questa crescita per replicarne il successo."
            )
        ]
    else:
        return []


def analizza_struttura_business(df_annuale: pd.DataFrame) -> List[str]:
    """
    Analizza la struttura complessiva del business su base annuale e genera insight strategici.

    Parameters:
        df_annuale (pd.DataFrame): DataFrame arricchito contenente i dati annuali. Deve includere le colonne:
            'Nome Piatto', 'Categoria', 'Ricavo Totale', 'Margine Totale', 'Marginalità (%)', 'Quantita Totale Anno'.

    Returns:
        list[str]: Lista di stringhe contenenti tutti gli insight strutturali rilevanti secondo la logica OIR.
    """
    insights_list: List[str] = []

    # --- Pareto Analysis (80/20 Rule) ---
    pareto_insight = _pareto_analysis(df_annuale)
    if pareto_insight:
        insights_list.append(pareto_insight)

    # --- Long-Tail Analysis ---
    long_tail_insight = _long_tail_analysis(df_annuale)
    if long_tail_insight:
        insights_list.append(long_tail_insight)

    # --- Workhorse Category Analysis ---
    workhorse_insights = _workhorse_category_analysis(df_annuale)
    insights_list.extend(workhorse_insights)

    # --- Gold Mine Category Analysis ---
    goldmine_insights = _goldmine_category_analysis(df_annuale)
    insights_list.extend(goldmine_insights)

    return insights_list


def _pareto_analysis(df: pd.DataFrame) -> Optional[str]:
    """
    Sub-routine: Analisi Pareto (80/20 Rule) sui prodotti.

    Parameters:
        df (pd.DataFrame): DataFrame annuale.

    Returns:
        Optional[str]: Insight OIR se trigger attivato, altrimenti None.
    """
    df_sorted = df.sort_values('Margine Totale', ascending=False).reset_index(drop=True)
    n_prodotti = len(df_sorted)
    n_top_20 = max(1, int(round(n_prodotti * 0.2)))
    total_margin = df_sorted['Margine Totale'].sum()
    if total_margin == 0:
        return None
    margin_top_20 = df_sorted.iloc[:n_top_20]['Margine Totale'].sum()
    perc_margine = margin_top_20 / total_margin

    if perc_margine > 0.8:
        return (
            "**Insight - Forte Concentrazione del Profitto (Principio di Pareto):**\n\n"
            f"* **Osservazione:** L'analisi mostra che circa l' {perc_margine*100:.0f}% del margine totale è generato da appena il 20% dei prodotti a menu.\n"
            "* **Implicazione:** Il business poggia su un nucleo di prodotti 'campioni' estremamente forte, ma questo crea una forte dipendenza strategica.\n"
            "* **Raccomandazione:** Proteggere questi prodotti chiave (qualità, disponibilità, pricing) è la priorità assoluta. Considerare strategie di marketing che usino questi prodotti come 'esca' per attirare clienti."
        )
    return None


def _long_tail_analysis(df: pd.DataFrame) -> Optional[str]:
    """
    Sub-routine: Analisi della 'Coda Lunga' improduttiva.

    Parameters:
        df (pd.DataFrame): DataFrame annuale.

    Returns:
        Optional[str]: Insight OIR se trigger attivato, altrimenti None.
    """
    df_sorted = df.sort_values('Margine Totale', ascending=True).reset_index(drop=True)
    n_prodotti = len(df_sorted)
    n_bottom_50 = max(1, int(round(n_prodotti * 0.5)))
    total_margin = df_sorted['Margine Totale'].sum()
    if total_margin == 0:
        return None
    margin_bottom_50 = df_sorted.iloc[:n_bottom_50]['Margine Totale'].sum()
    perc_margine = margin_bottom_50 / total_margin

    if perc_margine < 0.05:
        return (
            "**Insight - Presenza di una 'Coda Lunga' Improduttiva:**\n\n"
            f"* **Osservazione:** La metà meno performante del portafoglio prodotti (il 50%) genera complessivamente meno del {perc_margine*100:.1f}% del margine totale.\n"
            "* **Implicazione:** Un numero significativo di referenze a menu sta complicando le operazioni e i costi di magazzino, senza contribuire in modo significativo alla profittabilità.\n"
            "* **Raccomandazione:** Valutare uno snellimento strategico del menu. Considerare l'eliminazione dei prodotti meno performanti per ridurre la complessità e focalizzare i clienti sull'offerta più redditizia."
        )
    return None


def _workhorse_category_analysis(df: pd.DataFrame) -> List[str]:
    """
    Sub-routine: Analisi delle categorie 'Cavallo di Battaglia'.

    Parameters:
        df (pd.DataFrame): DataFrame annuale.

    Returns:
        list[str]: Lista di insight OIR per ogni categoria che attiva il trigger.
    """
    insights = []
    total_revenue = df['Ricavo Totale'].sum()
    total_margin = df['Margine Totale'].sum()
    if total_revenue == 0 or total_margin == 0:
        return insights

    cat_group = df.groupby('Categoria').agg({
        'Ricavo Totale': 'sum',
        'Margine Totale': 'sum'
    }).reset_index()

    for _, row in cat_group.iterrows():
        perc_ricavi = 100 * row['Ricavo Totale'] / total_revenue
        perc_margini = 100 * row['Margine Totale'] / total_margin
        if perc_ricavi - perc_margini > 15:
            insights.append(
                "**Insight - Categoria 'Cavallo di Battaglia' Identificata:**\n\n"
                f"* **Osservazione:** La categoria '{row['Categoria']}' è molto popolare, generando il {perc_ricavi:.0f}% dei ricavi totali, ma contribuisce solo per il {perc_margini:.0f}% ai margini complessivi.\n"
                "* **Implicazione:** Questa categoria attira un alto volume di clienti ma la sua bassa profittabilità media sta 'zavorrando' il margine totale dell'azienda.\n"
                "* **Raccomandazione:** Avviare un'iniziativa di ottimizzazione mirata su questa categoria. Analizzare i costi primi dei 3 prodotti più venduti al suo interno e valutare lievi e strategici aumenti di prezzo."
            )
    return insights


def _goldmine_category_analysis(df: pd.DataFrame) -> List[str]:
    """
    Sub-routine: Analisi delle categorie 'Miniera d'Oro'.

    Parameters:
        df (pd.DataFrame): DataFrame annuale.

    Returns:
        list[str]: Lista di insight OIR per ogni categoria che attiva il trigger.
    """
    insights = []
    total_revenue = df['Ricavo Totale'].sum()
    total_margin = df['Margine Totale'].sum()
    if total_revenue == 0 or total_margin == 0:
        return insights

    cat_group = df.groupby('Categoria').agg({
        'Ricavo Totale': 'sum',
        'Margine Totale': 'sum'
    }).reset_index()

    for _, row in cat_group.iterrows():
        perc_ricavi = 100 * row['Ricavo Totale'] / total_revenue
        perc_margini = 100 * row['Margine Totale'] / total_margin
        if perc_margini - perc_ricavi > 10:
            insights.append(
                "**Insight - Categoria 'Miniera d'Oro' Identificata:**\n\n"
                f"* **Osservazione:** La categoria '{row['Categoria']}' è un motore di profitto nascosto. Contribuisce solo per il {perc_ricavi:.0f}% ai ricavi, ma genera ben il {perc_margini:.0f}% dei margini totali.\n"
                "* **Implicazione:** Ogni vendita in questa categoria ha un impatto molto alto sulla profittabilità. Esiste un'enorme opportunità se si riesce ad aumentarne i volumi.\n"
                "* **Raccomandazione:** Implementare strategie di up-selling e cross-selling per guidare i clienti verso questa categoria. Formare il personale per proporla attivamente."
            )
    return insights