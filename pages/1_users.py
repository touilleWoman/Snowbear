import streamlit as st

from menu import menu_with_redirection
from utils.users_management import (
    delete_users,
    disable_users,
    enable_users,
    form_of_modifications,
    new_user,
    update_and_show_selected,
)
from utils.users_table import main_interaction

st.set_page_config(page_title="Users", layout="wide", initial_sidebar_state="auto")
menu_with_redirection()

# when a page is switched, all page related variables are reset, see page.py
page = st.session_state.page
page.switched("users")



tab1, tab2 = st.tabs([" 📋Users List ", "  ➕New User "])

with tab1:

    first_container = st.container(border=True)

    with first_container:
        main_interaction()

    # nb_selected is updated in the main_interaction function
    if page.nb_selected == 0:
        pass
    else:
        with first_container:
            col_modif, col_enable, col_disable, col_delete = st.columns([1, 1, 1, 6])

            # modify one user
            with col_modif:
                st.button(
                    st.session_state.transl["modify"],
                    help=st.session_state.transl["modify_condition"],
                    type="primary",
                    disabled=(page.nb_selected != 1)
                    or page.disabled["modify"],
                    on_click=page.switch_button,
                    args=["modify"],
                )
            with col_enable:
                st.button(
                    st.session_state.transl["enable"],
                    type="primary",
                    on_click=page.switch_button,
                    disabled=page.disabled["enable"],
                    args=["enable"],
                )
            with col_disable:
                st.button(
                    st.session_state.transl["disable"],
                    type="primary",
                    disabled=page.disabled["disable"],
                    on_click=page.switch_button,
                    args=["disable"],
                )
            with col_delete:
                st.button(
                    st.session_state.transl["delete"],
                    key="delete",
                    type="primary",
                    disabled=page.disabled["delete"],
                    on_click=page.switch_button,
                    args=["delete"],
                )

        second_container = st.container(border=True)
        with second_container:
            if page.clicks["modify"]:
                st.session_state.df_view = st.session_state.df_buffer.copy(deep=True)
                selected_row = st.session_state.df_view[
                    st.session_state.df_view["Action"]
                ]
                try:
                    with second_container:
                        form_of_modifications(selected_row.iloc[0])
                except Exception as e:
                    st.write(f"selected_row: {selected_row}")
                    st.write(e)

            # enable users
            if page.clicks["enable"]:
                selected_rows = update_and_show_selected(st.session_state.transl["enabling"])
                col_confirm, col_cancel = st.columns([0.1, 0.5])
                with col_confirm:
                    enable_confirmed = st.button(
                        "Confirm", key="confirm", type="primary"
                    )
                with col_cancel:
                    st.button(
                        "Cancel",
                        key="cancel",
                        type="secondary",
                        on_click=page.switch_button,
                        args=["enable"],
                    )
                if enable_confirmed:
                    enable_users(selected_rows)

            # disable users
            if page.clicks["disable"]:
                selected_rows = update_and_show_selected(st.session_state.transl["disabling"])
                col_confirm, col_cancel = st.columns([0.1, 0.5])
                with col_confirm:
                    disable_confirmed = st.button(
                        "Confirm", key="confirm", type="primary"
                    )
                with col_cancel:
                    st.button(
                        "Cancel",
                        key="cancel",
                        type="secondary",
                        on_click=page.switch_button,
                        args=["disable"],
                    )
                if disable_confirmed:
                    disable_users(selected_rows)

            # delete users
            if page.clicks["delete"]:
                selected_rows = update_and_show_selected(
                    st.session_state.transl["deletion"]
                )
                col_confirm, col_cancel = st.columns([0.1, 0.5])
                with col_confirm:
                    delete_confirmed = st.button(
                        "Confirm", key="confirm", type="primary"
                    )

                with col_cancel:
                    st.button(
                        "Cancel",
                        key="cancel",
                        type="secondary",
                        on_click=page.switch_button,
                        args=["delete"],
                    )
                if delete_confirmed:
                    delete_users(selected_rows)

    if page.message:
        for msg in page.message:
            if "Error" in msg:
                st.toast(f":red[{msg}]", icon="❌")
            else:
                st.toast(f":green[{msg}]", icon="✅")
        page.message = []

with tab2:
    st.header(st.session_state.transl["new_user"])
    container = st.container(border=True)
    with container:
        with st.form(key=page.form_id, border=False, clear_on_submit=True):
            # mandatary fields
            user_name = st.text_input("User name*")
            first_name = st.text_input(st.session_state.transl["first_name"] + "*")
            last_name = st.text_input(st.session_state.transl["last_name"] + "*")
            email = st.text_input("Email*")
            login = st.text_input("Login*")
            # optional fields
            password1 = st.text_input(st.session_state.transl["enter_pwd"], type="password", help="optinal")
            password2 = st.text_input(
                st.session_state.transl["confirm_pwd"], type="password", help="optinal"
            )
            if password1 != password2:
                msg = st.session_state.transl["pwd_mismatch"]
                st.toast(f":red[{msg}]", icon="❌")

            all_filled = all([user_name, first_name, last_name, email, login])
            submitted = st.form_submit_button(
                "Submit",
                type="primary",
            )

            if submitted and password1 == password2:
                if all_filled:
                    new_user(user_name, first_name, last_name, email, login, password1)
                else:
                    msg = st.session_state.transl["mandatory_fields"]
                    st.toast(f":red[{msg}]", icon="❌")
        st.button("Reset", type="secondary", on_click=page.clear_form)

    if page.message_tab2:
        if "Error" in page.message_tab2:
            st.toast(f":red[{page.message_tab2}]", icon="❌")
        else:
            st.toast(f":green[{page.message_tab2}]", icon="✅")
        page.message_tab2 = ""
