import streamlit as st
from snow_oauth import SnowOauth
from charge_translations import charge_translations

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

if 'translations' not in st.session_state:
    st.session_state.translations = {}

col1, col2 = st.columns([8, 1])
with col2:
    # default value will be 'fr' without selection
    selected_lang = st.selectbox("🌐", ["fr", "en"])

translations = charge_translations(selected_lang)
st.session_state.translations = translations

with col1:
    st.header(translations["greeting"])
    st.button("refresh")


def logout():
    if "snowpark_session" in st.session_state:
        st.session_state["snowpark_session"].close()
        st.session_state.clear()
        st.cache_data.clear()
        st.query_params.clear()
        st.success(translations["disconnected"])


def sidebar():
    session = st.session_state.snowpark_session
    user = session.sql("SELECT CURRENT_USER()").to_pandas()["CURRENT_USER()"].values[0]
    role = session.sql("SELECT CURRENT_ROLE()").to_pandas()["CURRENT_ROLE()"].values[0]
    with st.sidebar:
        st.write(translations["show_user"] + user)
        st.write(translations["show_role"] + role)
        st.button(translations["logout"], on_click=logout)


if "snowpark_session" not in st.session_state:
    label = translations["con_snowflake"]
    oauth = SnowOauth(label=label)
    oauth.start_session()
else:
    sidebar()
