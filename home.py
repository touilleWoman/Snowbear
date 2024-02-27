import streamlit as st
from snow_oauth import SnowOauth
from charge_translations import charge_translations
from menu import menu

if "snowpark_session" in st.session_state:
    sidebar_state = "expanded"
else:
    sidebar_state = "collapsed"

st.set_page_config(
    page_title="SNOWBEAR",
    page_icon="bear",
    layout="wide",
    initial_sidebar_state=sidebar_state,
)

if "translations" not in st.session_state:
    st.session_state.translations = {}

_col1, col2 = st.columns([8, 1])
with col2:
    # default value will be 'fr' without selection
    selected_lang = st.selectbox("🌐", ["fr", "en"])


translations = charge_translations(selected_lang)
st.session_state.translations = translations

st.header(translations["greeting"])
st.button("refresh")


if "snowpark_session" not in st.session_state:
    label = translations["con_snowflake"]
    oauth = SnowOauth(label=label)
    oauth.start_session()
else:
    menu()
