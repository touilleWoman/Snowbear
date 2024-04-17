import streamlit as st

from menu import menu_with_redirection
from utils.tools import clear_form
from utils.users_management import (
    delete_users,
    disable_users,
    enable_users,
    form_of_modifications,
    new_user,
    switch_button,
    update_and_show_selected,
)
from utils.users_table import show_df

st.set_page_config(page_title="Users", layout="wide", initial_sidebar_state="auto")

menu_with_redirection()


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

    first_container = st.container(border=True)

    with first_container:
        show_df()

    # nb_selected is updated in the show_df function
    if st.session_state.nb_selected == 0:
        pass
    else:
        with first_container:
            col_modif, col_enable, col_disable, col_delete = st.columns([1, 1, 1, 8])

            # modify one user
            with col_modif:
                st.button(
                    st.session_state.transl["modify"],
                    help=st.session_state.transl["modify_condition"],
                    type="primary",
                    disabled=(st.session_state.nb_selected != 1)
                    or st.session_state.disabled["modify"],
                    on_click=switch_button,
                    args=["modify"],
                )
            with col_enable:
                st.button(
                    st.session_state.transl["enable"],
                    type="primary",
                    on_click=switch_button,
                    disabled=st.session_state.disabled["enable"],
                    args=["enable"],
                )
            with col_disable:
                st.button(
                    st.session_state.transl["disable"],
                    type="primary",
                    disabled=st.session_state.disabled["disable"],
                    on_click=switch_button,
                    args=["disable"],
                )
            with col_delete:
                st.button(
                    st.session_state.transl["delete"],
                    key="delete",
                    type="primary",
                    disabled=st.session_state.disabled["delete"],
                    on_click=switch_button,
                    args=["delete"],
                )

        second_container = st.container(border=True)
        with second_container:
            if st.session_state.clicks["modify"]:
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
            if st.session_state.clicks["enable"]:
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
                        on_click=switch_button,
                        args=["enable"],
                    )
                if enable_confirmed:
                    enable_users(selected_rows)

            # disable users
            if st.session_state.clicks["disable"]:
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
                        on_click=switch_button,
                        args=["disable"],
                    )
                if disable_confirmed:
                    disable_users(selected_rows)

            # delete users
            if st.session_state.clicks["delete"]:
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
                        on_click=switch_button,
                        args=["delete"],
                    )
                if delete_confirmed:
                    delete_users(selected_rows)

    if st.session_state.message:
        for msg in st.session_state.message:
            if "Error" in msg:
                st.toast(f":red[{msg}]", icon="❌")
            else:
                st.toast(f":green[{msg}]", icon="✅")
        st.session_state.message = []

with tab2:
    if "message_tab2" not in st.session_state:
        st.session_state.message_tab2 = ""
    if "form_id" not in st.session_state:
        st.session_state.form_id = "new_user"
    st.header(st.session_state.transl["new_user"])
    container = st.container(border=True)
    with container:
        with st.form(key=st.session_state.form_id, border=False, clear_on_submit=True):
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
        st.button("Reset", type="secondary", on_click=clear_form)

    if st.session_state.message_tab2:
        msg = st.session_state.message_tab2
        if "Error" in msg:
            st.toast(f":red[{msg}]", icon="❌")
        else:
            st.toast(f":green[{msg}]", icon="✅")
        st.session_state.message_tab2 = ""
