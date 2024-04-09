import streamlit as st

from menu import menu
from footer import footer


if "snow_connector" in st.session_state:
    sidebar_state = "expanded"
else:
    sidebar_state = "collapsed"

st.set_page_config(
    page_title="SNOWBEAR",
    page_icon="🐻‍❄️",
    layout="wide",
    initial_sidebar_state=sidebar_state,
)
footer()

menu()
