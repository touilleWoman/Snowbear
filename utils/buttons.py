import streamlit as st

def switch_disable_button():
    st.session_state.disable_clicked = not st.session_state.disable_clicked
    # make sure other button sections are not open at the same time
    st.session_state.modify_clicked = False
    st.session_state.delete_clicked = False
    st.session_state.enable_clicked = False
    if st.session_state.disable_clicked:
        st.session_state.modify_type = "secondary"
        st.session_state.enable_type = "secondary"
        st.session_state.delete_type = "secondary"
    else:
        st.session_state.modify_type = "primary"
        st.session_state.enable_type = "primary"
        st.session_state.delete_type = "primary"

def switch_enable_button():
    st.session_state.enable_clicked = not st.session_state.enable_clicked
    st.session_state.modify_clicked = False
    st.session_state.delete_clicked = False
    st.session_state.disable_clicked = False
    if st.session_state.enable_clicked:
        st.session_state.modify_type = "secondary"
        st.session_state.disable_type = "secondary"
        st.session_state.delete_type = "secondary"
    else:
        st.session_state.modify_type = "primary"
        st.session_state.disable_type = "primary"
        st.session_state.delete_type = "primary"


def switch_delete_button():
    st.session_state.delete_clicked = not st.session_state.delete_clicked
    st.session_state.modify_clicked = False
    st.session_state.disable_clicked = False
    st.session_state.enable_clicked = False
    if st.session_state.delete_clicked:
        st.session_state.modify_type = "secondary"
        st.session_state.disable_type = "secondary"
        st.session_state.enable_type = "secondary"
    else:
        st.session_state.modify_type = "primary"
        st.session_state.disable_type = "primary"
        st.session_state.enable_type = "primary"

def switch_modify_button():
    st.session_state.modify_clicked = not st.session_state.modify_clicked
    st.session_state.disable_clicked = False
    st.session_state.delete_clicked = False
    st.session_state.enable_clicked = False
    if st.session_state.modify_clicked:
        st.session_state.disable_type = "secondary"
        st.session_state.delete_type = "secondary"
        st.session_state.enable_type = "secondary"
