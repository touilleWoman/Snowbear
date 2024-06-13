import itertools

import pandas as pd
import streamlit as st
from snowflake.connector.pandas_tools import write_pandas

from .admin_table import load_params_data


@st.cache_data
def load_rights_data():
    """ """
    cur = st.session_state.snow_connector.cursor()
    try:
        cur.execute("SELECT * from STREAMLIT.SNOWBEAR.rights")
        df = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])

    except Exception as e:
        st.error(e)
    finally:
        cur.close()
    return df


def new_rights_table_according_to_params(df, combinations):
    """
    Update the rights table based on the parameters table.

    This function filters the rights table to keep only the rows
    found in the combinations set. It then finds the missing combinations and adds
    them to the filtered rights table with the value rights = "-".
    Finally, it returns the updated rights table.

    Args:
        df (pandas.DataFrame): The original rights table.
        combinations (set): all possible combinations of environments, zones, and roles found in the parameters table.

    Returns:
        pandas.DataFrame: The updated rights table.
    """

    # Filter the DataFrame to keep only rows with combinations found in combinations_set
    df_filtered = df[
        df.apply(
            lambda row: (row["ENVIRONMENT"], row["ZONE"], row["ROLE"]) in combinations,
            axis=1,
        )
    ]

    # Find missing combinations and add them
    max_id = df["ID"].max()
    new_rows = []

    for combination in combinations:
        if df[
            (df["ENVIRONMENT"] == combination[0])
            & (df["ZONE"] == combination[1])
            & (df["ROLE"] == combination[2])
        ].empty:
            max_id += 1  # Update max_id for each new row
            new_rows.append(
                {
                    "ID": max_id,
                    "ENVIRONMENT": combination[0],
                    "ZONE": combination[1],
                    "ROLE": combination[2],
                    "RIGHTS": "-",
                }
            )

    # Create a DataFrame from new_rows and append it to df_filtered
    if new_rows:
        df_new_rows = pd.DataFrame(new_rows)
        df_filtered = pd.concat([df_filtered, df_new_rows], ignore_index=True)
    return df_filtered


def sync_rights_table_with_params():
    """
    Synchronize the rights table in Snowflake with the parameter settings.

    This function loads the current parameter settings and compares them with the existing rights
    table in Snowflake. If there are differences, it updates the rights table to reflect these settings:
    - It retains only those rights that match the parameter combinations.
    - It adds new default rights for parameter combinations that are missing in the rights table.
    - The rights table is then overwritten in Snowflake with the updated data.

    This ensures that the rights table in Snowflake is fully aligned with the latest parameter settings,
    supporting consistent access control and permissions management.

    Returns:
        pandas.DataFrame: The updated rights table, reflecting the latest parameter settings.
    """

    df_params = load_params_data()
    param_envs = set(df_params[df_params["TYPE"] == "Env"]["SHORT_DESC"])
    param_zones = set(df_params[df_params["TYPE"] == "Zone"]["SHORT_DESC"])
    param_roles = set(df_params[df_params["TYPE"] == "Role"]["SHORT_DESC"])

    df_rights = load_rights_data()
    rights_env = set(df_rights["ENVIRONMENT"].unique())
    rights_zone = set(df_rights["ZONE"].unique())
    rights_role = set(df_rights["ROLE"].unique())

    if all(
        [
            param_envs == rights_env,
            param_zones == rights_zone,
            param_roles == rights_role,
        ]
    ):
        # No need to update the rights table
        return df_rights

    combinations = set(itertools.product(param_envs, param_zones, param_roles))

    df = new_rights_table_according_to_params(df_rights, combinations)

    cur = st.session_state.snow_connector.cursor()
    try:
        cur.execute("TRUNCATE TABLE STREAMLIT.SNOWBEAR.rights")
        success, nchunks, nrows, _ = write_pandas(
            st.session_state.snow_connector,
            df,
            "RIGHTS",
            database="STREAMLIT",
            schema="SNOWBEAR",
        )
        print(f"Success: {success}, Chunks: {nchunks}, Rows inserted: {nrows}")
    except Exception as e:
        st.error(e)
    finally:
        if not success:
            st.error(
                "An error occurred while writing the new rights table to Snowflake."
            )
        load_rights_data.clear()
        cur.close()
        return df
    
    
def update_modified_rights_table(changes_list):

    cur = st.session_state.snow_connector.cursor()
    for change in changes_list:
        query = f"""
        UPDATE STREAMLIT.SNOWBEAR.RIGHTS
        SET RIGHTS = '{change["Value"]}'
        WHERE ENVIRONMENT = '{change["Enviroment"]}' AND ZONE = '{change["Zone"]}' AND "ROLE" = '{change["Role"]}'
        """
        try:
            cur.execute(query)
        except Exception as e:
            st.session_state.page.message.append(f"Error: {e}")
        else:
            st.session_state.page.message.append(f"{change} updated successfully")
            st.session_state.page.switch_button("modify")
        finally:
            cur.close()
            load_rights_data.clear()
            st.session_state.page.clicks["modify"] = False
            st.rerun()
            