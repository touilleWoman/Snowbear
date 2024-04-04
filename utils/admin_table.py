import pandas as pd
import streamlit as st

@st.cache_data
def load_params_data():
    cur = st.session_state.snow_connector.cursor()
    try:
        cur.execute("SELECT * from STREAMLIT.SNOWBEAR.parameterization")
        df = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
        df["Action"] = False

    except Exception as e:
        st.error(e)
    finally:
        cur.close()
    return df

def get_types():
    df = load_params_data()
    types = df.TYPE.unique()
    return types