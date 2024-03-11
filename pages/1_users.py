import streamlit as st

import snowflake.connector
from pandas import DataFrame
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
def load_data():
    cur = st.session_state.snow_connector.cursor()
    try:
        cur.execute(
            "SELECT LOGIN_NAME, FIRST_NAME, LAST_NAME FROM snowflake.account_usage.users;"
        )
        df = DataFrame(cur.fetchall())
    except snowflake.connector.errors.ProgrammingError as e:
        # default error message
        st.error(e)
        # customer error message
        st.error(
            "Error {0} ({1}): {2} ({3})".format(e.errno, e.sqlstate, e.msg, e.sfqid)
        )
    finally:
        cur.close()
    return df


def create_newuser(login, first_name, last_name, password):
    cur = st.session_state.snow_connector.cursor()
    try:
        cur.execute(
            f"CREATE USER {login} PASSWORD={password} FIRST_NAME={first_name} LAST_NAME={last_name}"
        )
    except snowflake.connector.errors.ProgrammingError as e:
        # default error message
        st.write(e)
        # customer error message
        st.write(
            "Error {0} ({1}): {2} ({3})".format(e.errno, e.sqlstate, e.msg, e.sfqid)
        )
    except Exception as e:
        st.warning(e)
    else:
        st.success(cur.fetchone()[0])
    finally:
        cur.close()


def switch_newuser_button():
    if st.session_state.newuser_button_clicked is True:
        st.session_state.newuser_button_clicked = False
    else:
        st.session_state.newuser_button_clicked = True

def show_users_list():
    st.header(st.session_state.translations["users_list"])
    try:
        df = load_data()
        df[3] = False
        edited_user_df = st.data_editor(
            df,
            column_config={
                "0": "login",
                "1": "first name",
                "2": "last name",
                "3": st.column_config.CheckboxColumn(
                    "Action", help="Select one user to modify", default=False
                ),
            },
            hide_index=True,
        )
    except Exception as e:
        st.write(e)

if "snow_connector" not in st.session_state:
    st.warning("Not connected to snowflake")
else:
    if "newuser_button_clicked" not in st.session_state:
        st.session_state.newuser_button_clicked = False

    tab1, tab2= st.tabs([" 🔎Users List ", "  ➕New User "])
    with tab1:
        show_users_list()
    with tab2:
    # st.button("New User", type="primary", on_click=switch_newuser_button)

    # if st.session_state.newuser_button_clicked:
        st.header("Create a new user")
        with st.form("new_user"):
            first_name = st.text_input("First name")
            last_name = st.text_input("last name")
            login = st.text_input("login")
            password1 = st.text_input("Enter password", type="password")
            password2 = st.text_input("Confirm password", type="password")
            if password1 != password2:
                st.error("Passwords do not match. Please try again.")
            submitted = st.form_submit_button("Submit", type="primary")
            if submitted:
                if password1 == password2:
                    create_newuser(login, first_name, last_name, password1)

        # st.button("Cancel", on_click=switch_newuser_button)
