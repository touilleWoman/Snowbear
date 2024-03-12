import streamlit as st

from menu import menu


st.set_page_config(page_title="Databases", layout="wide", initial_sidebar_state="auto")

menu()

_col1, col2 = st.columns([8, 1])
with col2:
    # default value will be 'fr' without selection
    selected_lang = st.selectbox("🌐", ["fr", "en"])

if "snow_connector" not in st.session_state:
    st.warning("Not connected to snowflake")
else:
    type = st.selectbox("Type", ("ENV", "ZONE"))
    valeur = st.selectbox("Valeur", ("DEV", "QUA", "PPR", "PRD"))
    description= st.text_input("Description")
    