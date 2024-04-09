import streamlit as st

from footer import footer
from menu import authenticated_menu
from snow_oauth import SnowOauth


def unauthenticated():
    col_hardis, col_partner = st.columns([1, 6])
    with col_hardis:
        st.image("./images/logo_hardis.png", width=200)
    with col_partner:
        st.image("./images/place_holder.jpg", width=200)

    st.header("❄️ Welcome to your SNOW BEAR ❄️")
    st.header("❄️ Bienvenue à votre SNOW BEAR ❄️")
    oauth = SnowOauth(label="Se connecter à Snowflake")
    oauth.start_session()


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


if "snow_connector" not in st.session_state:
    unauthenticated()
else:
    authenticated_menu()

footer()
