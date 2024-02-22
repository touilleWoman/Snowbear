import streamlit as st
from snow_oauth import SnowOauth
import gettext

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

_ = gettext.gettext


col1, col2 = st.columns([8, 1])
with col2:
    selected_lang = 'fr'
    selected_lang = st.selectbox('', ['en', 'fr'])
    if selected_lang == "en":
        localizator = gettext.translation(
            "messages", localedir="locales", languages=[selected_lang]
        )
        localizator.install()
        _ = localizator.gettext








with col1:
    st.header(_("Bienvenue à votre SNOW BEAR"))
    st.button("refresh")


def logout():
    if "snowpark_session" in st.session_state:
        st.session_state["snowpark_session"].close()
        st.session_state.clear()
        st.cache_data.clear()
        st.query_params.clear()
        st.success(_("Déconnecté avec succès."))


def sidebar():
    session = st.session_state.snowpark_session
    user = session.sql("SELECT CURRENT_USER()").to_pandas()["CURRENT_USER()"].values[0]
    role = session.sql("SELECT CURRENT_ROLE()").to_pandas()["CURRENT_ROLE()"].values[0]
    with st.sidebar:
        st.write(_("Utilisateur: ") + user)
        st.write(_("Role: ") + role)
        st.button(_("Déconnexion"), on_click=logout)


if "snowpark_session" not in st.session_state:
    label = _("Se connecter à Snowflake")
    oauth = SnowOauth(label=label)
    oauth.start_session()
else:
    sidebar()
