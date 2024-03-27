import streamlit as st

from menu import menu
from users_table import show_df, delete_users, new_user, form_of_modifications

st.set_page_config(page_title="Users", layout="wide", initial_sidebar_state="auto")

menu()

def switch_delete_button():
    st.session_state.delete_clicked = not st.session_state.delete_clicked
    # make sure the delete section and modify section are not both open
    st.session_state.modify_clicked = False
    
def switch_modify_button():
    st.session_state.modify_clicked = not st.session_state.modify_clicked
    # make sure the delete section and modify section are not both open
    st.session_state.delete_clicked = False
    
def clear_form():
    st.session_state.form_id +="1"
    
if "snow_connector" not in st.session_state:
    st.warning("Not connected to snowflake")
else:
    tab1, tab2 = st.tabs([" 📋Users List ", "  ➕New User "])

    with tab1:
        if "nb_selected" not in st.session_state:
            st.session_state.nb_selected = 0
        if "delete_clicked" not in st.session_state:
            st.session_state.delete_clicked = False
        if "modify_clicked" not in st.session_state:
            st.session_state.modify_clicked = False
          
        show_df()
        if "message" not in st.session_state:
            st.session_state.message = []

        # nb_selected is updated in the show_df function
        if st.session_state.nb_selected > 0:

                
            col_modif, col_enable, col_disable, col_delete = st.columns([1, 1, 1, 8])
            
            # modify one user
            with col_modif:
                st.button(
                    "Modify",
                    help="select one user to modify",
                    type="primary",
                    disabled=(st.session_state.nb_selected != 1),
                    on_click=switch_modify_button,
                )
            with col_enable:
                st.button("Enable", type="primary")
            with col_disable:
                st.button("Disable", type="primary")
            with col_delete:
                st.button("Delete", key="delete", type="primary", on_click=switch_delete_button)
                
            if st.session_state.modify_clicked:
                st.session_state.df_view = st.session_state.df_buffer.copy(deep=True)
                selected_row = st.session_state.df_view[st.session_state.df_view["Action"]]
                try:
                    form_of_modifications(selected_row.iloc[0])
                except Exception as e:
                    st.write(f"selected_row: {selected_row}")
                    st.write(e)
                
            # delete users    

            if st.session_state.delete_clicked:
                st.session_state.df_view = st.session_state.df_buffer.copy(deep=True)
                selected_rows = st.session_state.df_view[st.session_state.df_view["Action"]]
                st.warning("Do you confirm the deletion of the following users?")
                st.write(selected_rows)
                col_confirm, col_cancel = st.columns([0.1, 0.5])
                with col_confirm:
                    if st.button("Confirm", key = "confirm", type="primary"):
                        delete_users(selected_rows)
                with col_cancel:
                    st.button("Cancel", key="cancel", type="secondary", on_click=switch_delete_button)
                    
        # message created in delete_users() 
        if st.session_state.message:
            for msg in st.session_state.message:
                if "Error" in msg:
                    st.error(msg, icon="❌")
                else:
                    st.success(msg, icon="✅")
            del st.session_state["message"]

    with tab2:
        if "form_id" not in st.session_state:
            st.session_state.form_id = "new_user"
        st.header("Create a new user")
        container = st.container(border=True)
        with container:
            with st.form(key = st.session_state.form_id, border=False, clear_on_submit=True):
                # mandatary fields
                user_name = st.text_input("User name*")
                first_name = st.text_input("First name*")
                last_name = st.text_input("last name*")
                email = st.text_input("email*")
                login = st.text_input("login*")
                # optional fields
                password1 = st.text_input("Enter password", type="password", help="optinal")
                password2 = st.text_input("Confirm password", type="password", help="optinal")
                if password1 != password2:
                    st.error("Passwords do not match. Please try again.")  
            
                all_filled = all ([user_name, first_name, last_name, email, login])
                submitted = st.form_submit_button("Submit", type="primary")

                if submitted and password1 == password2:
                    if all_filled :
                        new_user(user_name, first_name, last_name, email, login, password1)
                    else:
                        st.error("Fields marked with * are mandatory.")
            st.button("Cancel", type="secondary", on_click=clear_form)

