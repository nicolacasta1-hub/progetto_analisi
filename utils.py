# utils.py

import streamlit as st

def local_css(file_name):
    """
    Carica un file CSS locale e lo applica all'applicazione Streamlit.
    """
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
