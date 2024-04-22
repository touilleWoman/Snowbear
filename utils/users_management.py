import html

import streamlit as st

from .users_table import load_user_data


page = st.session_state.page


def clear_cache_then_rerun():
    load_user_data.clear()
    st.session_state["df_view"] = load_user_data()
    st.session_state["df_buffer"] = load_user_data()
    st.session_state.page.nb_selected = 0
    st.rerun()


def new_user(user_name, first_name, last_name, email, login, password=""):
    user_name = html.escape(user_name)
    first_name = html.escape(first_name)
    last_name = html.escape(last_name)
    email = html.escape(email)
    login = html.escape(login)
    if password:
        password = html.escape(password)

    cur = st.session_state.snow_connector.cursor()
    try:
        query = f"""
            CREATE USER "{user_name}" FIRST_NAME="{first_name}" LAST_NAME="{last_name}" EMAIL="{email}" LOGIN_NAME="{login}"
            """
        if password:
            query += f" PASSWORD='{password}'"
        cur.execute(query)

    except Exception as e:
        st.session_state.page.message_tab2 = f"Error: {e}"
    else:
        st.session_state.page.message_tab2 = cur.fetchone()[0]
    finally:
        cur.close()
        clear_cache_then_rerun()


def disable_users(selected_rows):
    msgs = []
    try:
        for _index, row in selected_rows.iterrows():
            name = row["name"]
            cur = st.session_state.snow_connector.cursor()
            query = f"""ALTER USER "{name}" SET DISABLED = TRUE;
                        """
            cur.execute(query)
            # succcess messages will be displayed after the rerun
            msgs.append(f"USER {name} disabled")
    except Exception as e:
        page.message.append(f"Error: {e}")
    else:
        page.switch_button("disable")
        page.message.extend(msgs)
    finally:
        cur.close()
        clear_cache_then_rerun()


def enable_users(selected_rows):
    try:
        msgs = []
        for _index, row in selected_rows.iterrows():
            name = row["name"]
            cur = st.session_state.snow_connector.cursor()
            sql = f"""ALTER USER "{name}" SET DISABLED = FALSE;
                        """
            cur.execute(sql)
            # succcess messages will be displayed after the rerun
            msgs.append(f"USER {name} enabled")
    except Exception as e:
        page.message.append(f"Error: {e}")
    else:
        page.switch_button("enable")
        page.message.extend(msgs)
    finally:
        cur.close()
        clear_cache_then_rerun()


def delete_users(selected_rows):
    try:
        msgs = []
        for _index, row in selected_rows.iterrows():
            name = row["name"]
            cur = st.session_state.snow_connector.cursor()
            cur.execute(
                f"""DROP USER "{name}"
                        """
            )
            msgs.append(cur.fetchone()[0])
    except Exception as e:
        page.message.append(f"Error: {e}")
    else:
        page.switch_button("delete")
        page.message.extend(msgs)
    finally:
        cur.close()
        clear_cache_then_rerun()


def modify_user(name, modified_fields):
    try:
        msgs = []
        for label, modif in modified_fields.items():
            modif = html.escape(modif)
            cur = st.session_state.snow_connector.cursor()
            query = f"""ALTER USER "{name}" SET {label} = "{modif}"
                        """
            cur.execute(query)
            msgs.append(f"USER {name} altered: {label} changed to {modif}")
    except Exception as e:
        page.message.append(f"Error: {e}")
    else:
        page.switch_button("modify")
        page.message.extend(msgs)
    finally:
        cur.close()
        clear_cache_then_rerun()


def password_validation(password1, password2):
    conditions = [
        (password1 != password2, st.session_state.transl["password_mismatch"]),
        (len(password1) < 8, st.session_state.transl["pwd_len"]),
        (
            not any(char.isupper() for char in password1),
            st.session_state.transl["pwd_uppercase"],
        ),
        (
            not any(char.islower() for char in password1),
            st.session_state.transl["pwd_lowercase"],
        ),
        (
            not any(char.isdigit() for char in password1),
            st.session_state.transl["pwd_digit"],
        ),
    ]

    valid = True
    for condition, message in conditions:
        if condition:
            st.toast(f":red[{message}]", icon="❌")
            valid = False
    return valid


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


def update_and_show_selected(action_label):
    st.session_state.df_view = st.session_state.df_buffer.copy(deep=True)
    selected_rows = st.session_state.df_view[st.session_state.df_view["Action"]]
    selected_rows = selected_rows.drop(columns=["Action"])
    if st.session_state.transl["key"] == "en":
        st.warning(f"Do you confirm the {action_label} of the following users?")
    else:
        st.warning(f"Confirmez-vous {action_label} des utilisateurs suivants ?")
    st.dataframe(
        selected_rows,
        column_config={
            "name": "User name",
            "login_name": "Login name",
            "first_name": st.session_state.transl["first_name"],
            "last_name": st.session_state.transl["last_name"],
            "disabled": st.session_state.transl["disabled"],
            "email": "Email",
        },
    )
    return selected_rows
