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


def delete_admin_params(selected_rows):
    page = st.session_state.page
    try:
        ids = tuple(selected_rows["ID"])
        cur = st.session_state.snow_connector.cursor()
        query = (
            "DELETE FROM STREAMLIT.SNOWBEAR.parameterization WHERE id IN ({})".format(
                ", ".join(['?'] * len(ids))
            )
        )
        cur.execute(query, ids)
    except Exception as e:
        page.message.append(f"Error: {e}")
    else:
        msg = f"{selected_rows["SHORT_DESC"]} deleted"
        page.message.append(msg)
        page.switch_button("delete")
    finally:
        cur.close()
        load_params_data.clear()
        st.rerun()


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


def show_selected(selected_rows, action_label):
    selected_rows = selected_rows.drop(columns=["ACTION"])
    if st.session_state.transl["key"] == "en":
        st.warning(f"Do you confirm the {action_label} of the following parameters?")
    else:
        st.warning(f"Confirmez-vous {action_label} des paramètres suivants ?")
    st.dataframe(
        selected_rows,
        column_config={"MODIFIER": st.session_state.transl["modifier"]},
    )
