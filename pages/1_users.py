import streamlit as st
import snowflake.connector
from charge_translations import charge_translations
from menu import menu
from pandas import DataFrame

st.set_page_config(page_title="Users", layout="wide", initial_sidebar_state="auto")

menu()

_col1, col2 = st.columns([8, 1])
with col2:
    # default value will be 'fr' without selection
    selected_lang = st.selectbox("🌐", ["fr", "en"])


translations = charge_translations(selected_lang)
st.session_state.translations = translations


@st.cache_data
def load_data():
    cur = st.session_state.snow_connector.cursor()
    try:
        cur.execute("SELECT LOGIN_NAME, FIRST_NAME, LAST_NAME FROM snowflake.account_usage.users;")
        df = DataFrame(cur.fetchall())
        st.write(df)
    except snowflake.connector.errors.ProgrammingError as e:
        # default error message
        print(e)
        # customer error message
        print('Error {0} ({1}): {2} ({3})'.format(e.errno, e.sqlstate, e.msg, e.sfqid))
    finally:
        cur.close()
    return "bla"


if "snow_connector" in st.session_state:
    st.subheader(st.session_state.translations["users"])
    try:
        df = load_data()
            # Display tables in Streamlit
        edited_df = st.data_editor(
            df, column_config={"Users": "Users of Snowflake"}, num_rows="dynamic"
        )

    except Exception as e:
        st.write(e)