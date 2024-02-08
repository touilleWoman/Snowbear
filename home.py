import streamlit as st
from st_snowauth import snowauth_session

st.set_page_config(
    page_title="SNOWBEAR", page_icon="bear", initial_sidebar_state="auto"
)


st.markdown("## This (and above) is always seen")
session = snowauth_session(label="Click to login to Snowflake")
st.markdown("## This (and below) is only seen after authentication")