import streamlit as st
import pandas as pd

@st.cache_data
def load_rights_data():
    """
    """
    cur = st.session_state.snow_connector.cursor()
    try:
        cur.execute("SELECT * from STREAMLIT.SNOWBEAR.rights")
        df = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

    except Exception as e:
        st.error(e)
    finally:
        cur.close()
    return df
