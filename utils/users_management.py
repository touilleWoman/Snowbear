import streamlit as st
import html
from .users_table import load_user_data


def switch_button(label):
    """	
    switch the button to the opposite state
    When one button is clicked, all the others are set to False
    with type "secondary"
    """
    clicks = st.session_state.clicks
    types = st.session_state.types
    clicks[label] = not clicks[label]
    for key in clicks.keys():
        if key != label:
            clicks[key] = False
    if clicks[label]:
        for key in types.keys():
            if key != label:
                types[key] = "secondary"
    else:
        for key in types.keys():
            types[key] = "primary"



def clear_cache_then_rerun():
    load_user_data.clear()
    st.session_state["df_view"] = load_user_data()
    st.session_state["df_buffer"] = load_user_data()
    st.session_state.nb_selected = 0
    st.rerun()


def new_user(user_name, first_name, last_name, email, login, password=""):
    cur = st.session_state.snow_connector.cursor()
    try:
        query = f"""
            CREATE USER "{user_name}" FIRST_NAME="{first_name}" LAST_NAME="{last_name}" EMAIL="{email}" LOGIN_NAME="{login}"
            """
        if password:
            query += f" PASSWORD='{password}'"
        query = html.escape(query)
        cur.execute(query)
        
    except Exception as e:
        st.session_state.message_tab2 =f"Error: {e}"
    else:
        st.session_state.message_tab2 = cur.fetchone()[0]
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
        switch_button("disable")
    finally:
        cur.close()
        clear_cache_then_rerun()


def enable_users(selected_rows):
    try:
        for _index, row in selected_rows.iterrows():
            name = row["name"]
            cur = st.session_state.snow_connector.cursor()
            sql = f"""ALTER USER "{name}" SET DISABLED = FALSE;
                        """
            cur.execute(sql)
            # succcess messages will be displayed after the rerun
            st.session_state.message.append(f"{cur.fetchone()[0]} {sql}")
    except Exception as e:
        st.session_state.message.append(f"Error: {e}")
    else:
        switch_button("enable")
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
        switch_button("delete")
    finally:
        cur.close()
        clear_cache_then_rerun()


def modify_user(name, modified_fields):
    try:
        for label, modif in modified_fields.items():
            cur = st.session_state.snow_connector.cursor()
            query = f"""ALTER USER "{name}" SET {label} = "{modif}"
                        """
            query = html.escape(query)
            cur.execute(query)
            st.session_state.message.append(f"{cur.fetchone()[0]} {query}")
    except Exception as e:
        st.session_state.message.append(f"Error: {e}")
    else:
        switch_button("modify")
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
