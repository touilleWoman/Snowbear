import streamlit as st
import gettext

_ = gettext.gettext

@st.cache_data
def load_tata():
    session = st.session_state.snowpark_session
    users = session.sql("SHOW USERS")
    breakpoint()
    return users.collect()


if "snowpark_session" in st.session_state:
    st.set_page_config(page_title='Users', layout='wide')
    st.subheader(_('Utilisateurs'))
    df = load_tata()
    # Display tables in Streamlit
    edited_df = st.data_editor(df, column_config={"Users": "Users of Snowflake"}, num_rows="dynamic")
