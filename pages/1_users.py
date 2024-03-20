import streamlit as st

from menu import menu
from users_table import load_user_data, show_df
# from users_table import UsersTable 

st.set_page_config(page_title="Users", layout="wide", initial_sidebar_state="auto")

menu()






if "snow_connector" not in st.session_state:
    st.warning("Not connected to snowflake")
else:
    if "one_user_selected" not in st.session_state:
        st.session_state.one_user_selected = False


    tab1, tab2 = st.tabs([" 📋Users List ", "  ➕New User "])

    with tab1:

        show_df()   
        
        
        # if "users_table" not in st.session_state:
        #     st.session_state.users_table = UsersTable()
        # users_table = st.session_state.users_table
        # users_table.show_table()
        
        
        # if st.session_state.one_user_selected is True:
        # if users_table.active_buttons is True:
        #     left, right = st.columns([0.3, 0.7])
        #     with left:
        #         delete_clicked = st.button("Delete", type="primary")
        #         if delete_clicked:
        #             users_table.delete_user()
        #     with right:
        #         st.button("Modify", type="primary")
            # option = st.selectbox(
            #     "Select one user to modify or multipe users to delete",
            #     ("Modify", "Delete"),
            #     index=None,
            #     placeholder="Select your action...",
            # )
            # if option == "Delete":
            #     users_table.delete_user()
            # if option == "Modify":
            #     users_table.modify_user()                


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
