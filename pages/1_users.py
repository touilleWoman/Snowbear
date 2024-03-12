import streamlit as st

from charge_translations import charge_translations
from menu import menu
from users_table import UsersTable 

st.set_page_config(page_title="Users", layout="wide", initial_sidebar_state="auto")

menu()

_col1, col2 = st.columns([8, 1])
with col2:
    # default value will be 'fr' without selection
    selected_lang = st.selectbox("🌐", ["fr", "en"])


st.session_state.translations = charge_translations(selected_lang)
if selected_lang != st.session_state.selected_lang:
    st.session_state.selected_lang = selected_lang
    st.rerun()





if "snow_connector" not in st.session_state:
    st.warning("Not connected to snowflake")
else:
    if "user_action_box" not in st.session_state:
        st.session_state.user_action_box = False

    tab1, tab2 = st.tabs([" 🔎Users List ", "  ➕New User "])

    with tab1:
        users_table = UsersTable()
        # st.info('Select ONE user to delete or modify', icon="ℹ️")
        if st.session_state.user_action_box is True:
            option = st.selectbox(
                "Select one user to modify or multipe users to delete",
                ("Modify", "Delete"),
                index=None,
                placeholder="Select your action...",
            )
            if option == "Delete":
                users_table.delete_user()
            if option == "Modify":
                users_table.modify_user()                


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
                    # create_newuser(login, first_name, last_name, password1)
                    users_table.new_user(login, first_name, last_name, password1)

        # st.button("Cancel", on_click=switch_newuser_button)
