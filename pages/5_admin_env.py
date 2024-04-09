import streamlit as st

from menu import menu_with_redirection

from utils.admin_table import show_selected_params

st.set_page_config(page_title="Environments", layout="wide", initial_sidebar_state="auto")

menu_with_redirection()
    
st.title(st.session_state.translations["parameters"])
show_selected_params("Env")
    
    