import streamlit as st

from menu import menu_with_redirection

from utils.admin_table import show_selected_params, admin_new_type
from utils.tools import clear_form

st.set_page_config(page_title="Environments", layout="wide", initial_sidebar_state="auto")

menu_with_redirection()
    
tab1, tab2 = st.tabs([" 📋Env List ", "  ➕New Env "])
with tab1:
    show_selected_params("Env")
    
with tab2:
    st.header(st.session_state.translations["create_env"])
    container = st.container(border=True)
    if "form_id" not in st.session_state:
        st.session_state.form_id = "new_env"
    with container:
        with st.form(
            key=st.session_state.form_id, border=False, clear_on_submit=True
        ):
            short_desc = st.text_input("Short descpription*")
            long_des = st.text_input("Long description*")
            all_filled = short_desc and long_des
            submitted = st.form_submit_button("Submit", type="primary")
            if submitted:
                if all_filled:
                    admin_new_type("Env", short_desc, long_des)
                else:
                    st.toast(":red[Please fill all the fields]", icon="❌")
        st.button("Reset", type="secondary", on_click=clear_form)
