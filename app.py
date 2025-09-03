import streamlit as st
import pandas as pd

# Passo 1.2: Dare un titolo alla nostra applicazione
st.title("Progetto di Analisi Strategica - v0.1")
st.write("Benvenuto nel nostro primo strumento di analisi.")

# Passo 1.3: Creare un set di dati di prova
# (In futuro, questi dati arriveranno da un file o da un database)
dati_di_prova = {
    'Piatto': ['Pizza Margherita', 'Spaghetti Carbonara', 'Tagliata di Manzo', 'Tiramisù', 'Acqua Minerale', 'Vino Rosso'],
    'Categoria': ['Pizze', 'Primi', 'Secondi', 'Dessert', 'Bevande', 'Bevande'],
    'Costo Primo': [2.5, 3.0, 7.0, 2.0, 0.5, 4.0],
    'Prezzo Vendita': [7.0, 10.0, 18.0, 5.0, 2.0, 12.0],
    'Quantita Vendute': [150, 110, 80, 90, 200, 60]
}

# Creiamo un DataFrame di Pandas con i nostri dati di prova
df = pd.DataFrame(dati_di_prova)


# Passo 1.4: Mostrare i dati sulla pagina web
st.header("Dati di Vendita (Esempio)")
st.write("Ecco la tabella di dati che useremo come base per le nostre analisi:")
st.dataframe(df)
