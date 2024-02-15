import streamlit as st
from snow_oauth import snowauth_session

st.set_page_config(
    page_title="SNOWBEAR", page_icon="bear", initial_sidebar_state="auto"
)

st.header("Bienvenue à votre SNOW BEAR")


if 'snowpark_session' not in st.session_state:
    snowauth_session(label="login to Snowflake")
else:
    st.write('snowpark session is here:')
    st.write(st.session_state.snowpark_session)





