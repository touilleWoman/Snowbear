import streamlit as st

from menu import menu
from users_table import show_df, delete_users, new_user, modify_user

st.set_page_config(page_title="Users", layout="wide", initial_sidebar_state="auto")

menu()

def switch_delete_button():
    st.session_state.delete_clicked = not st.session_state.delete_clicked

if "snow_connector" not in st.session_state:
    st.warning("Not connected to snowflake")
else:
    tab1, tab2 = st.tabs([" 📋Users List ", "  ➕New User "])

    with tab1:
        if "nb_selected" not in st.session_state:
            st.session_state.nb_selected = 0
        if "delete_clicked" not in st.session_state:
            st.session_state.delete_clicked = False
            
        show_df()

        # nb_selected is updated in the show_df function
        if st.session_state.nb_selected > 0:
            col_modif, col_delete = st.columns([0.3, 0.7])
            with col_modif:
                modified = st.button(
                    "Modify",
                    help="select one user to modify",
                    type="primary",
                    disabled=st.session_state.nb_selected != 1,
                )
                if modified:
                    modify_user()
            with col_delete:
                st.button("Delete", type="primary", on_click=switch_delete_button)
                if st.session_state.delete_clicked:
                    selected_rows = st.session_state.df_buffer[st.session_state.df_buffer["Action"]]
                    st.warning("Do you confirm the deletion of the following users?")
                    st.write(selected_rows)
                    col_confirm, col_cancel = st.columns([0.1, 0.5])
                    with col_confirm:
                        if st.button("Confirm", type="primary"):
                            delete_users(selected_rows)
                    with col_cancel:
                        st.button("Cancel", type="secondary", on_click=switch_delete_button)

    with tab2:
        st.header("Create a new user")
        with st.form("new_user"):
            login = st.text_input("login")
            first_name = st.text_input("First name")
            last_name = st.text_input("last name")
            password1 = st.text_input("Enter password", type="password")
            password2 = st.text_input("Confirm password", type="password")
            if password1 != password2:
                st.error("Passwords do not match. Please try again.")
            submitted = st.form_submit_button("Submit", type="primary")
            if submitted:
                if password1 == password2:
                    new_user(login, first_name, last_name, password1)

        # st.button("Cancel", on_click=switch_newuser_button)
