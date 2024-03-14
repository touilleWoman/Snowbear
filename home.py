import streamlit as st
from charge_translations import charge_translations
from menu import menu
from snow_oauth import SnowOauth

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


_col1, col2 = st.columns([8, 1])
# st.header(translations["greeting"])
st.header("❄️ Welcome to your SNOW BEAR ❄️")
st.header("❄️ Bienvenue à votre SNOW BEAR ❄️")


if "snow_connector" not in st.session_state:
    oauth = SnowOauth(label="Se connecter à Snowflake")
    oauth.start_session()
else:
    menu()




with col2:
    st.image("./images/Logo_Hardis_Group.png", width=200, caption="Powered by")
