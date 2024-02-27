import streamlit as st

from charge_translations import charge_translations
from menu import menu

st.set_page_config(page_title="Users", layout="wide", initial_sidebar_state="auto")

menu()

_col1, col2 = st.columns([8, 1])
with col2:
    # default value will be 'fr' without selection
    selected_lang = st.selectbox("🌐", ["fr", "en"])


translations = charge_translations(selected_lang)
st.session_state.translations = translations


@st.cache_data
def load_tata():
    session = st.session_state.snowpark_session
    users = session.sql("SHOW USERS")
    return users.collect()


if "snowpark_session" in st.session_state:
    st.subheader(st.session_state.translations["users"])
    df = load_tata()
    # Display tables in Streamlit
    edited_df = st.data_editor(
        df, column_config={"Users": "Users of Snowflake"}, num_rows="dynamic"
    )
