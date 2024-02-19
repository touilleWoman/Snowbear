import streamlit as st
from snow_oauth import SnowOauth

st.set_page_config(
    page_title="SNOWBEAR", page_icon="bear", initial_sidebar_state="auto"
)

st.header("Bienvenue à votre SNOW BEAR")
st.button("refraiche")


def logout():
    if "snowpark_session" in st.session_state:
        st.session_state["snowpark_session"].close()
        for key in st.session_state.keys():
            del st.session_state[key]
        st.query_params.pop("code")
        st.query_params.pop("state")


if "snowpark_session" not in st.session_state:
    oauth = SnowOauth(label="login to Snowflake")
    oauth.start_session()
else:
    st.sidebar.button("Logout", on_click=logout)

    # st.session_state.snowpark_session.sql("USE DATABASE SNOWFLAKE_SAMPLE DATA")
    # tables_result = st.session_state.snowpark_session.sql("SHOW TABLES")

    # # Display tables in Streamlit
    # if tables_result:
    #     st.write("Tables in Snowflake database:")
    #     for row in tables_result.collect():
    #         st.write(row["name"])
    # else:
    #     st.write("No tables found in Snowflake database.")
