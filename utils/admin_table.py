import pandas as pd
import html
import streamlit as st
from menu import get_user

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

def show_selected_params(type):
    df = load_params_data()
    filtered_df = df[df["TYPE"] == type]
    st.data_editor(
        filtered_df,
        hide_index=True,
        column_config={"MODIFIER": st.session_state.transl["modifier"]},
    )


def admin_new_type(type, short_desc, long_desc):
    short_desc = html.escape(short_desc)
    long_desc = html.escape(long_desc)
    cur = st.session_state.snow_connector.cursor()
    try:
        # use qmark binding to avoid sql injection
        cur.execute(
            "INSERT INTO STREAMLIT.SNOWBEAR.parameterization (TYPE, SHORT_DESC, LONG_DESC, MODIFIER, MODIFICATION) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP())",
            (type, short_desc, long_desc, get_user()),
        )
    except Exception as e:
        st.error(e)
    finally:
        cur.close()
        load_params_data.clear()
        st.rerun()
