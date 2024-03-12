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
if "user_action_box" not in st.session_state:
    st.session_state.user_action_box = False


@st.cache_data
def load_user_data():
    cur = st.session_state.snow_connector.cursor()
    try:
        cur.execute(
            # "SELECT LOGIN_NAME, FIRST_NAME, LAST_NAME FROM snowflake.account_usage.users;"
            "SHOW USERS"
        )
        cur.execute(
            """
            select "login_name", "first_name", "last_name", 
            from table(result_scan(last_query_id())) order by "login_name"
            """
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


def show_user_action_box():
    st.session_state.user_action_box = True


def users_df():
    st.header(st.session_state.translations["users_list"])
    try:
        df = load_user_data()
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
            on_change=show_user_action_box,
        )
    except Exception as e:
        st.write(e)
    return edited_user_df


def delete_user(df):
    selected_rows = df[df.iloc[:, 3]]
    if len(selected_rows) != 1:
        st.error("Select ONE user only, Please recheck your selection")
    else:
        name, first_name, last_name, _selection = selected_rows.values[0]
        st.warning(f"Do you confirm the deletion of {first_name} {last_name}")
        if st.button("Confirm", type="primary"):
            cur = st.session_state.snow_connector.cursor()
            try:
                cur.execute(f"DROP USER {name}")
            except snowflake.connector.errors.ProgrammingError as e:
                # default error message
                st.write(e)
                # customer error message
                st.write(
                    "Error {0} ({1}): {2} ({3})".format(
                        e.errno, e.sqlstate, e.msg, e.sfqid
                    )
                )
            except Exception as e:
                st.warning(e)
            else:
                st.success(cur.fetchone()[0])
                load_user_data.clear()
                st.rerun()
            finally:
                cur.close()


if "snow_connector" not in st.session_state:
    st.warning("Not connected to snowflake")
else:
    tab1, tab2 = st.tabs([" 🔎Users List ", "  ➕New User "])

    with tab1:
        edited_df = users_df()
        # st.info('Select ONE user to delete or modify', icon="ℹ️")
        if st.session_state.user_action_box is True:
            option = st.selectbox(
                "You can modify one user or delete users",
                ("Modify", "Delete"),
                index=None,
                placeholder="Select your action...",
            )
            if option == "Delete":
                delete_user(edited_df)

    with tab2:
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
