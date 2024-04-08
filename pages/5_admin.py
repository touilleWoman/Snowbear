import streamlit as st

from menu import menu
from utils.admin_table import show_selected_params

st.set_page_config(page_title="Admin", layout="wide", initial_sidebar_state="auto")




if "snow_connector" not in st.session_state:
    st.warning("Non connecté à Snowflake")
else:
    menu(show_admin_radio=True)
    
    st.title(st.session_state.translations["parameters"])
    show_selected_params(st.session_state.type)
    
    