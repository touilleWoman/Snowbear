import pandas as pd
import streamlit as st

def switch_disable_button():
    st.session_state.disable_clicked = not st.session_state.disable_clicked
    # make sure other button sections are not open at the same time
    st.session_state.modify_clicked = False
    st.session_state.delete_clicked = False
    st.session_state.enable_clicked = False
    if st.session_state.disable_clicked:
        st.session_state.modify_type = "secondary"
        st.session_state.enable_type = "secondary"
        st.session_state.delete_type = "secondary"
    else:
        st.session_state.modify_type = "primary"
        st.session_state.enable_type = "primary"
        st.session_state.delete_type = "primary"

def switch_enable_button():
    st.session_state.enable_clicked = not st.session_state.enable_clicked
    st.session_state.modify_clicked = False
    st.session_state.delete_clicked = False
    st.session_state.disable_clicked = False
    if st.session_state.enable_clicked:
        st.session_state.modify_type = "secondary"
        st.session_state.disable_type = "secondary"
        st.session_state.delete_type = "secondary"
    else:
        st.session_state.modify_type = "primary"
        st.session_state.disable_type = "primary"
        st.session_state.delete_type = "primary"


def switch_delete_button():
    st.session_state.delete_clicked = not st.session_state.delete_clicked
    st.session_state.modify_clicked = False
    st.session_state.disable_clicked = False
    st.session_state.enable_clicked = False
    if st.session_state.delete_clicked:
        st.session_state.modify_type = "secondary"
        st.session_state.disable_type = "secondary"
        st.session_state.enable_type = "secondary"
    else:
        st.session_state.modify_type = "primary"
        st.session_state.disable_type = "primary"
        st.session_state.enable_type = "primary"

def switch_modify_button():
    st.session_state.modify_clicked = not st.session_state.modify_clicked
    st.session_state.disable_clicked = False
    st.session_state.delete_clicked = False
    st.session_state.enable_clicked = False
    if st.session_state.modify_clicked:
        st.session_state.disable_type = "secondary"
        st.session_state.delete_type = "secondary"
        st.session_state.enable_type = "secondary"

@st.cache_data
def load_user_data():
    cur = st.session_state.snow_connector.cursor()
    try:
        cur.execute("SHOW USERS")
        rows = cur.fetchall()
        df = pd.DataFrame(rows, columns=[desc[0] for desc in cur.description])
        selected_columns = [
            "name",
            "login_name",
            "first_name",
            "last_name",
            "email",
            "disabled",
        ]
        df = df[selected_columns]
        df["Action"] = False

    except Exception as e:
        st.error(e)
    finally:
        cur.close()
    return df


def filter_df(df, text_search):
    m1 = df["name"].str.contains(text_search, case=False)
    m2 = df["login_name"].str.contains(text_search, case=False)
    m3 = df["first_name"].str.contains(text_search, case=False)
    m4 = df["last_name"].str.contains(text_search, case=False)
    m5 = df["email"].str.contains(text_search, case=False)
    filtered_df = df[m1 | m2 | m3 | m4 | m5]
    return filtered_df


def update_nb_selected_in_session_state():
    """
    check if the user selected at least one user
    """

    df = st.session_state.df_buffer
    st.session_state.nb_selected = len(df[df["Action"]])


def save_selection_in_buffer():
    """
    user clicked one selectbox,
    in dataframe: st.session_state.df_buffer
    update the column 'Action' with the new value(True/False)
    """

    df = st.session_state.df_view.copy(deep=True)
    modifs = st.session_state.users_modifs["edited_rows"]
    for index, value in modifs.items():
        df.iloc[index, -1] = value["Action"]
        name = df.iloc[index]["name"]
        st.session_state.df_buffer.loc[
            st.session_state.df_buffer["name"] == name, "Action"
        ] = value["Action"]
    update_nb_selected_in_session_state()


def show_df():
    """
    if user search for a user, then show filtered dataframe + selected users
    else show the original dataframe with selected users

    !!!important information:
    - df_view is the dataframe that the user see
    - df_buffer is the dataframe which store the selections
    why this complexity? because streamlit has a specific way to handle dataframes
    each time we click on a selectbox, the application rerun from the top, but on the front end
    it doesn't always reload the dataframe to avoid flashing effect,
    it will reload when the parameters of st.data_editor change.
    So If we change the value of df_view each time we click, the page will flash each time we click.
    To avoid this, we use df_buffer to store the selections,
    and we update the df_view only when we use the filter or when we take off the filer

    """

    if "df_view" not in st.session_state:
        st.session_state.df_view = load_user_data()
        st.session_state.df_buffer = load_user_data()

    if "last_search" not in st.session_state:
        st.session_state.last_search = ""

    text_search = st.text_input("🔍")

    # use a filter
    if text_search and text_search != st.session_state.last_search:
        df = st.session_state.df_buffer.copy(deep=True)
        selected_rows = df[df["Action"]]

        # take off selected rows from the dataframe to avoid duplicates
        df = df.drop(selected_rows.index)

        df = filter_df(df, text_search)

        # combine selected rows with the filtered dataframe
        df = pd.concat([df, selected_rows])

        # update the view
        st.session_state.df_view = df

    # delete the filter, so update the view
    if not text_search and st.session_state.last_search:
        st.session_state.df_view = st.session_state.df_buffer.copy(deep=True)

    st.session_state.last_search = text_search

    st.data_editor(
        st.session_state.df_view,
        key="users_modifs",
        column_config={"name": "user name"},
        on_change=save_selection_in_buffer,
    )


def clear_cache_then_rerun():
    load_user_data.clear()
    st.session_state["df_view"] = load_user_data()
    st.session_state["df_buffer"] = load_user_data()
    st.session_state.nb_selected = 0
    st.rerun()


def new_user(user_name, first_name, last_name, email, login, password=""):
    cur = st.session_state.snow_connector.cursor()
    try:
        command = f"""
            CREATE USER "{user_name}" FIRST_NAME="{first_name}" LAST_NAME="{last_name}" EMAIL="{email}" LOGIN_NAME="{login}"
            """
        if password:
            command += f" PASSWORD='{password}'"
        cur.execute(command)
    except Exception as e:
        st.warning(e)
    else:
        st.success(cur.fetchone()[0], icon="✅")
        # clear cache to make sure new created user is displayed

    finally:
        cur.close()
        clear_cache_then_rerun()

def disable_users(selected_rows):
    try:
        for _index, row in selected_rows.iterrows():
            name = row["name"]
            cur = st.session_state.snow_connector.cursor()
            sql = f"""ALTER USER "{name}" SET DISABLED = TRUE;
                        """
            cur.execute(sql)
            # succcess messages will be displayed after the rerun
            st.session_state.message.append(f"{cur.fetchone()[0]} {sql}")
    except Exception as e:
        st.session_state.message.append(f"Error: {e}")
    else:
        switch_disable_button()
    finally:
        cur.close()
        clear_cache_then_rerun()


def enable_users(selected_rows):
    try:
        for _index, row in selected_rows.iterrows():
            name = row["name"]
            cur = st.session_state.snow_connector.cursor()
            sql =f"""ALTER USER "{name}" SET DISABLED = FALSE;
                        """
            cur.execute(sql)
            # succcess messages will be displayed after the rerun
            st.session_state.message.append(f"{cur.fetchone()[0]} {sql}")
    except Exception as e:
        st.session_state.message.append(f"Error: {e}")
    else:
        switch_enable_button()
    finally:
        cur.close()
        clear_cache_then_rerun()

def delete_users(selected_rows):
    try:
        for _index, row in selected_rows.iterrows():
            name = row["name"]
            cur = st.session_state.snow_connector.cursor()
            cur.execute(
                f"""DROP USER "{name}"
                        """
            )
            # succcess messages will be displayed after the rerun
            st.session_state.message.append(cur.fetchone()[0])
    except Exception as e:
        st.session_state.message.append(f"Error: {e}")
    else:
        switch_delete_button()
    finally:
        cur.close()
        clear_cache_then_rerun()


def modify_user(name, modified_fields):
    try:
        for label, modif in modified_fields.items():
            cur = st.session_state.snow_connector.cursor()
            sql = f"""ALTER USER "{name}" SET {label} = "{modif}"
                        """
            cur.execute(sql)
            st.session_state.message.append(f"{cur.fetchone()[0]} {sql}")
    except Exception as e:
        st.session_state.message.append(f"Error: {e}")
    else:
        switch_modify_button()
    finally:
        cur.close()
        clear_cache_then_rerun()


def password_validation(password1, password2):
    if password1 != password2:
        st.error("Passwords do not match. Please try again.")
        return False
    if password1 and len(password1) < 8:
        st.error("Password must be at least 8 characters long")
        return False
    if not any([char.isupper() for char in password1]):
        st.error("At least one uppercase letter is required for password")
        return False
    if not any([char.islower() for char in password1]):
        st.error("At least one lowercase letter is required for password")
        return False
    if not any([char.isdigit() for char in password1]):
        st.error("At least one digit is required for password")
        return False
    return True


def form_of_modifications(selected_row):
    name, login, first, last, email, _disabled, _action = selected_row
    change_password = st.toggle(f"change user {first} {last}'S password")

    with st.form("modify_user"):
        st.text_input("user name", value=name, disabled=True)
        m_login = st.text_input("login name", value=login)
        m_first = st.text_input("First name", value=first)
        m_last = st.text_input("last name", value=last)
        m_email = st.text_input("email", value=email)
        password1 = ""
        if change_password:
            password1 = st.text_input("new password", type="password")
            password2 = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Submit", type="primary")
        if password1 and not password_validation(password1, password2):
            return
        if not submitted:
            return

        pairs = [
            (login, m_login, "LOGIN_NAME"),
            (first, m_first, "FIRST_NAME"),
            (last, m_last, "LAST_NAME"),
            (email, m_email, "EMAIL"),
        ]
        modified_fields = {label: m_x for x, m_x, label in pairs if m_x != x}
        if password1:
            modified_fields["PASSWORD"] = password1
        modify_user(name, modified_fields)
