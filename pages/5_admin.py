import streamlit as st

from menu import menu
from utils.admin_table import load_params_data

st.set_page_config(page_title="Admin", layout="wide", initial_sidebar_state="auto")

menu()



if "snow_connector" not in st.session_state:
    st.warning("Non connecté à Snowflake")
else:
    st.title(st.session_state.translations["parameters"])
    df = load_params_data()
    st.data_editor(
        df,
        hide_index=True,
    )