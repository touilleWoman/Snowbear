import streamlit as st

from menu import menu_with_redirection
from utils.tools import clear_form
from utils.users_management import (
    delete_users,
    disable_users,
    enable_users,
    new_user,
    form_of_modifications,
    switch_button,
)
from utils.users_table import show_df

st.set_page_config(page_title="Users", layout="wide", initial_sidebar_state="auto")

menu_with_redirection()


def update_and_show_selected(action_label):
    st.session_state.df_view = st.session_state.df_buffer.copy(deep=True)
    selected_rows = st.session_state.df_view[st.session_state.df_view["Action"]]
    selected_rows = selected_rows.drop(columns=["Action"])
    st.warning(f"Do you confirm the {action_label} of the following users?")
    st.write(selected_rows)
    return selected_rows


tab1, tab2 = st.tabs([" 📋Users List ", "  ➕New User "])

with tab1:
    if "clicks" not in st.session_state:
        labels = ["delete", "modify", "disable", "enable"]
        st.session_state.clicks = {label: False for label in labels}
        st.session_state.disabled = {label: False for label in labels}
            # st.session_state.types = {label: "primary" for label in labels}
    if "message" not in st.session_state:
        st.session_state.message = []
    if "nb_selected" not in st.session_state:
        st.session_state.nb_selected = 0

    with st.container(border=True):
        show_df()

    with st.container(border=True):
        # nb_selected is updated in the show_df function
        if st.session_state.nb_selected == 0:
            pass
        else:
            col_modif, col_enable, col_disable, col_delete = st.columns([1, 1, 1, 8])

            # modify one user
            with col_modif:
                st.button(
                    "Modify",
                    help="select one user to modify",
                    type="primary",
                    disabled=(st.session_state.nb_selected != 1) or st.session_state.disabled["modify"],
                    on_click=switch_button,
                    args=["modify"],
                )
            with col_enable:
                st.button(
                    "Enable",
                    type="primary",
                    on_click=switch_button,
                        disabled=st.session_state.disabled["enable"],
                    args=["enable"],
                )
            with col_disable:
                st.button(
                    "Disable",
                    type="primary",
                        disabled=st.session_state.disabled["disable"],
                    on_click=switch_button,
                    args=["disable"],
                )
            with col_delete:
                st.button(
                    "Delete",
                    key="delete",
                    type="primary",
                        disabled=st.session_state.disabled["delete"],
                    on_click=switch_button,
                    args=["delete"],
                )

            if st.session_state.clicks["modify"]:
                st.session_state.df_view = st.session_state.df_buffer.copy(deep=True)
                selected_row = st.session_state.df_view[st.session_state.df_view["Action"]]
                try:
                    form_of_modifications(selected_row.iloc[0])
                except Exception as e:
                    st.write(f"selected_row: {selected_row}")
                    st.write(e)

            # enable users
            if st.session_state.clicks["enable"]:
                selected_rows = update_and_show_selected("enabling")
                col_confirm, col_cancel = st.columns([0.1, 0.5])
                with col_confirm:
                    enable_confirmed = st.button("Confirm", key="confirm", type="primary")
                with col_cancel:
                    st.button(
                        "Cancel",
                        key="cancel",
                        type="secondary",
                        # on_click=switch_enable_button,
                        on_click=switch_button,
                        args=["enable"],
                    )
                if enable_confirmed:
                    enable_users(selected_rows)
                    
            # disable users
            if st.session_state.clicks["disable"]:
                selected_rows = update_and_show_selected("disabling")
                col_confirm, col_cancel = st.columns([0.1, 0.5])
                with col_confirm:
                    disable_confirmed = st.button("Confirm", key="confirm", type="primary")
                with col_cancel:
                    st.button(
                        "Cancel",
                        key="cancel",
                        type="secondary",
                        # on_click=switch_disable_button,
                        on_click=switch_button,
                        args=["disable"],
                    )
                if disable_confirmed:
                    disable_users(selected_rows)

                # delete users

            if st.session_state.clicks["delete"]:
                selected_rows = update_and_show_selected("deletion")
                col_confirm, col_cancel = st.columns([0.1, 0.5])
                with col_confirm:
                    delete_confirmed = st.button("Confirm", key="confirm", type="primary")
                        
                with col_cancel:
                    st.button(
                        "Cancel",
                        key="cancel",
                        type="secondary",
                        # on_click=switch_delete_button,
                        on_click=switch_button,
                        args=["delete"],
                    )
                if delete_confirmed:
                    delete_users(selected_rows)

        if st.session_state.message:
            for msg in st.session_state.message:
                if "Error" in msg:
                    st.error(msg, icon="❌")
                else:
                    st.success(msg, icon="✅")
            st.session_state.message = []

with tab2:
    if "message_tab2" not in st.session_state:
        st.session_state.message_tab2 = ""
    if "form_id" not in st.session_state:
        st.session_state.form_id = "new_user"
    st.header("Create a new user")
    container = st.container(border=True)
    with container:
        with st.form(key=st.session_state.form_id, border=False, clear_on_submit=True):
            # mandatary fields
            user_name = st.text_input("User name*")
            first_name = st.text_input("First name*")
            last_name = st.text_input("last name*")
            email = st.text_input("email*")
            login = st.text_input("login*")
            # optional fields
            password1 = st.text_input("Enter password", type="password", help="optinal")
            password2 = st.text_input(
                "Confirm password", type="password", help="optinal"
            )
            if password1 != password2:
                st.error("Passwords do not match. Please try again.")

            all_filled = all([user_name, first_name, last_name, email, login])
            submitted = st.form_submit_button(
                "Submit",
                type="primary",
            )

            if submitted and password1 == password2:
                if all_filled:
                    new_user(user_name, first_name, last_name, email, login, password1)
                else:
                    st.error("Fields marked with * are mandatory.")

                new_user(user_name, first_name, last_name, email, login, password1)
        st.button("Reset", type="secondary", on_click=clear_form)

    if st.session_state.message_tab2:
        msg = st.session_state.message_tab2
        if "Error" in msg:
            st.error(msg, icon="❌")
        else:
            st.success(msg, icon="✅")
        st.session_state.message_tab2 = ""
