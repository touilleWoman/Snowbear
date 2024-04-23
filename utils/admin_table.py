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


def main_interaction(df):
    """
    table and buttons for the page env/zone/roles
    
    :return: The updated DataFrame after editing.
    """

    sorted_df = df.sort_values(by=["ORDRE"])
    updated_df = st.data_editor(
        sorted_df,
        hide_index=True,
        column_order=("ORDRE", "ID", "TYPE", "SHORT_DESC", "LONG_DESC", "MODIFIER", "MODIFICATION", "ACTION"),
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
        short_des = selected_rows["SHORT_DESC"].astype(str).str.cat(sep=", ")
        msg = f"{short_des} deleted successfully"
        page.message.append(msg)
        page.switch_button("delete")
    finally:
        cur.close()
        load_params_data.clear()
        st.rerun()


def admin_new_type(df, type, short_desc, long_desc):
    short_desc = html.escape(short_desc)
    long_desc = html.escape(long_desc)
    cur = st.session_state.snow_connector.cursor()
    try:
        ordre = int(df["ORDRE"].max()) + 1
        # use qmark binding to avoid sql injection
        cur.execute(
            "INSERT INTO STREAMLIT.SNOWBEAR.parameterization (ORDRE, TYPE, SHORT_DESC, LONG_DESC, MODIFIER, MODIFICATION) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP())",
            (ordre, type, short_desc, long_desc, get_user()),
        )
    except Exception as e:
        st.session_state.page.message_tab2 = f"Error: {e}"
    else:
        st.session_state.page.message_tab2 = f"{short_desc} added successfully"
    finally:
        cur.close()
        load_params_data.clear()
        st.rerun()


def show_selected(selected_rows, action_label):
    selected_rows = selected_rows.drop(columns=["ACTION", "ID", "ORDRE"])
    if st.session_state.transl["key"] == "en":
        st.warning(f"Do you confirm the {action_label} of the following parameters?")
    else:
        st.warning(f"Confirmez-vous {action_label} des paramètres suivants ?")
    st.dataframe(
        selected_rows,
        hide_index=True,
        column_config={"MODIFIER": st.session_state.transl["modifier"]},
    )
