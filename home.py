import streamlit as st
from snow_oauth import snowauth_session 

st.set_page_config(
    page_title="SNOWBEAR", page_icon="bear", initial_sidebar_state="auto"
)

st.header("Bienvenue à votre SNOW BEAR")

session = snowauth_session(label="login to Snowflake")
st.success('Authentification réussie !')

