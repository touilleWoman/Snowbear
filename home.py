import streamlit as st
from snow_oauth import SnowOauth

if "snowpark_session" in st.session_state:
    sidebar_state = "expanded"
else:
    sidebar_state = "collapsed"

st.set_page_config(
    page_title="SNOWBEAR", page_icon="bear", initial_sidebar_state=sidebar_state
)

st.header("Bienvenue à votre SNOW BEAR")
st.button("refresh")


def logout():
    if "snowpark_session" in st.session_state:
        st.session_state["snowpark_session"].close()
        st.session_state.clear()
        st.cache_data.clear()
        st.query_params.clear()
        st.success("Déconnecté avec succès.")


def sidebar():
    session = st.session_state.snowpark_session
    user = session.sql("SELECT CURRENT_USER()").to_pandas()["CURRENT_USER()"].values[0]
    role = session.sql("SELECT CURRENT_ROLE()").to_pandas()["CURRENT_ROLE()"].values[0]
    with st.sidebar:
        st.write(f"Utilisateur: {user}")
        st.write(f"Role: {role}")
        st.button("Déconnexion", on_click=logout)


if "snowpark_session" not in st.session_state:
    oauth = SnowOauth(label="login to Snowflake")
    oauth.start_session()
else:
    sidebar()
