import html

import pandas as pd
import streamlit as st

from menu import get_user


@st.cache_data
def load_params_data():
    """
    Load parameterization table, add columns 'Action'
    """
    cur = st.session_state.snow_connector.cursor()
    try:
        cur.execute("SELECT * from STREAMLIT.SNOWBEAR.parameterization")
        df = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
        df["ACTION"] = False

    except Exception as e:
        st.error(e)
    finally:
        cur.close()
    return df


def main_interaction(type):
    """
    table and buttons for the page env/zone/roles
    """
    
    df = load_params_data()
    filtered_df = df[df["TYPE"] == type]

    updated_df = st.data_editor(
        filtered_df,
        hide_index=True,
        column_config={"MODIFIER": st.session_state.transl["modifier"]},
    )
    return updated_df


def update_nb_selected_in_session_state():
    """
    check if the user selected at least one user
    """

    df = st.session_state.df_env_buffer
    st.session_state.nb_selected = len(df[df["Action"]])


def save_selection_in_buffer():
    """
    user clicked one selectbox,
    in dataframe: st.session_state.df_env_buffer
    update the column 'Action' with the new value(True/False)
    """

    df = st.session_state.df_env.copy(deep=True)
    modifs = st.session_state.env_modifs["edited_rows"]
    for index, value in modifs.items():
        df.iloc[index, -1] = value["ACTION"]
        name = df.iloc[index]["name"]
        st.session_state.df_env_buffer.loc[
            st.session_state.df_env_buffer["name"] == name, "Action"
        ] = value["Action"]
    update_nb_selected_in_session_state()


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
