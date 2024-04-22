import streamlit as st

from menu import menu_with_redirection

from utils.admin_table import main_interaction, admin_new_type

st.set_page_config(page_title="Environments", layout="wide", initial_sidebar_state="auto")

# when a page is switched, all page related variables are reset, see page.py
page = st.session_state.page
page.switched("environments")

menu_with_redirection()
    
tab1, tab2 = st.tabs([" 📋Env List ", "  ➕New Env "])

with tab1:
    first_container = st.container(border=True)
    with first_container:
        df = main_interaction("Env")
        nb_selected = len(df[df["ACTION"]])
        st.write(nb_selected)
        
    # nb_selected is updated in the show_selected_params function
    if nb_selected == 0:
        pass
    else:
        with first_container:
            col_modif, col_delete = st.columns([1, 4])
            with col_modif:
                st.button(
                    st.session_state.transl["modify"],
                    help=st.session_state.transl["modify_condition"],
                    type="primary",
                    disabled=(nb_selected != 1)
                    or page.disabled["modify"],
                    on_click=page.switch_button,
                    args=["modify"],
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
                
    
with tab2:
    st.header(st.session_state.transl["create_env"])
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
                    msg = st.session_state.transl["mandatory_fields"]
                    st.toast(f":red[{msg}]", icon="❌")
        st.button("Reset", type="secondary", on_click=page.clear_form)
