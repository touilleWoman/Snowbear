import streamlit as st
from snow_oauth import SnowOauth

st.set_page_config(
    page_title="SNOWBEAR", page_icon="bear", initial_sidebar_state="auto"
)

st.header("Bienvenue à votre SNOW BEAR")
st.button("refresh")


def logout():
    if "snowpark_session" in st.session_state:
        st.session_state["snowpark_session"].close()
        for key in st.session_state.keys():
            del st.session_state[key]
        st.query_params.pop("code")
        st.query_params.pop("state")
        st.success("Déconnecté avec succès.")


def sidebar():
    session = st.session_state.snowpark_session
    user = session.sql("SELECT CURRENT_USER()").to_pandas()["CURRENT_USER()"].values[0]
    role = session.sql("SELECT CURRENT_ROLE()").to_pandas()["CURRENT_ROLE()"].values[0]
    with st.sidebar:
        st.write(f"Utilisateur: {user}")
        st.write(f"Role: {role}")
        st.button("Déconnexion", on_click=logout)


@st.cache_data
def load_tata():
    session = st.session_state.snowpark_session
    return session.sql("SHOW USERS").collect()


if "snowpark_session" not in st.session_state:
    oauth = SnowOauth(label="login to Snowflake")
    oauth.start_session()
else:
    sidebar()

    df = load_tata()
    # Display tables in Streamlit
    edited_df = st.data_editor(
        df, column_config={"Users": "Users of Snowflake"}, num_rows="dynamic"
    )
