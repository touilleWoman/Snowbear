import streamlit as st

from menu import menu_with_redirection
from utils.admin_table import (
    admin_new_type,
    delete_admin_params,
    load_params_data,
    main_interaction,
    show_selected,
    form_of_modifications,
)

st.set_page_config(page_title="Zones", layout="wide", initial_sidebar_state="auto")
menu_with_redirection()

# when a page is switched, all page related variables are reset, see page.py
page = st.session_state.page
page.switched("admin_zones")

    
tab1, tab2 = st.tabs([" 📋Zone List ", "  ➕New Zone "])

df_params = load_params_data()
df_zone = df_params[df_params["TYPE"] == "Zone"]

with tab1:
    first_container = st.container(border=True)
    with first_container:
        df = main_interaction(df_zone)
        nb_selected = len(df[df["ACTION"]])
        
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

        second_container = st.container(border=True)
        with second_container:
            selected_rows = df[df["ACTION"]]
            
            if page.clicks["modify"]:
                try:
                    form_of_modifications(selected_rows.iloc[0])
                except Exception as e:
                    st.write(e)

            # delete users
            if page.clicks["delete"]:
                show_selected(selected_rows, st.session_state.transl["deletion"])
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
                    delete_admin_params(selected_rows)

    if page.message:
        for msg in page.message:
            if "Error" in msg:
                st.toast(f":red[{msg}]", icon="❌")
            else:
                st.toast(f":green[{msg}]", icon="✅")
        page.message = []
              
    
with tab2:
    st.header(st.session_state.transl["create_zone"])
    container = st.container(border=True)
    prefilled_order = int(df_zone["ORDER"].max()) + 1
    with container:
        with st.form(
            key=page.form_id, border=False, clear_on_submit=True
        ):
            order = st.text_input("Order*", value=prefilled_order)
            short_desc = st.text_input("Short descpription*")
            long_des = st.text_input("Long description*")
            all_filled = short_desc and long_des and order
            submitted = st.form_submit_button("Submit", type="primary")
            if submitted:
                if all_filled:
                    admin_new_type(df_zone,"Zone", short_desc, long_des, order)
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