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

    sorted_df = df.sort_values(by=["ORDER"])
    updated_df = st.data_editor(
        sorted_df,
        hide_index=True,
        column_order=(
            "ORDER",
            "ID",
            "TYPE",
            "SHORT_DESC",
            "LONG_DESC",
            "MODIFIER",
            "MODIFICATION",
            "ACTION",
        ),
        column_config={"MODIFIER": st.session_state.transl["modifier"]},
    )
    return updated_df


def delete_admin_params(selected_rows):
    page = st.session_state.page
    try:
        ids = tuple(selected_rows["ID"])
        cur = st.session_state.snow_connector.cursor()
        # use format binding(client side), becasue qmark binding do not support "IN" operator
        query = (
            "DELETE FROM STREAMLIT.SNOWBEAR.parameterization WHERE id IN ({})".format(
                ", ".join(["?"] * len(ids))
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


def admin_new_type(df, type, short_desc, long_desc, order):
    short_desc = html.escape(short_desc)
    long_desc = html.escape(long_desc)
    cur = st.session_state.snow_connector.cursor()
    try:
        # use qmark binding(server side) to avoid sql injection
        cur.execute(
            """INSERT INTO STREAMLIT.SNOWBEAR.parameterization (TYPE, SHORT_DESC, LONG_DESC, MODIFIER, MODIFICATION, "ORDER") VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP(), ?)""",
            (type, short_desc, long_desc, get_user(), order),
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
    selected_rows = selected_rows.drop(columns=["ACTION", "ID", "ORDER"])
    if st.session_state.transl["key"] == "en":
        st.warning(f"Do you confirm the {action_label} of the following parameters?")
    else:
        st.warning(f"Confirmez-vous {action_label} des paramètres suivants ?")
    st.dataframe(
        selected_rows,
        hide_index=True,
        column_config={"MODIFIER": st.session_state.transl["modifier"]},
    )


def form_of_modifications(row):
    short_desc = row["SHORT_DESC"]
    long_desc = row["LONG_DESC"]
    order = row["ORDER"]
    id = row["ID"]
    with st.form(key="modify_env"):
        st.text_input("ID", value=id, disabled=True)
        m_order = st.text_input("Order", value=order)
        m_short_desc = st.text_input("Short descpription", value=short_desc)
        m_long_desc = st.text_input("Long description", value=long_desc)
        submitted = st.form_submit_button("Submit", type="primary")
        if not submitted:
            return
        try:
            m_order = int(m_order)
        except ValueError:
            st.toast(f":red[{st.session_state.transl['order_validation']}]", icon="❌")
            return
        m_short_desc = html.escape(m_short_desc)
        m_long_desc = html.escape(m_long_desc)
        pairs = [
            (order, m_order, "\"ORDER\""), # ORDER is a reserved keyword in SQL, so it needs to be escaped
            (short_desc, m_short_desc, "SHORT_DESC"),
            (long_desc, m_long_desc, "LONG_DESC"),
        ]
        modified_fields = {label: m_x for x, m_x, label in pairs if m_x != x}
        if len(modified_fields) == 0:
            st.toast(f":red[{st.session_state.transl['no_modif']}]", icon="❌")
            return
        modify_admin_params(id, modified_fields)


def modify_admin_params(id, modified_fields):
    id = int(id)
    page = st.session_state.page
    try:
        sql_set_clause = ', '.join(f"{key} = ?" for key in modified_fields.keys())
        sql_values = tuple(modified_fields.values())
        sql_query = f"UPDATE STREAMLIT.SNOWBEAR.PARAMETERIZATION SET {sql_set_clause} WHERE ID = ?"
        sql_values += (id,)  # Append the ID to the values tuple for the WHERE clause
        
        cur = st.session_state.snow_connector.cursor()
        # use qmark binding to avoid sql injection
        cur.execute(sql_query, sql_values)
    except Exception as e:
        page.message.append(f"Error: {e}")
    else:
        page.message.append(f"Parameter with id {id} is modified successfully")
        page.switch_button("modify")
        load_params_data.clear()
        st.rerun()
    finally:
        cur.close()
