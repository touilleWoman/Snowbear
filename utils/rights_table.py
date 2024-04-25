import streamlit as st
import pandas as pd
import itertools

from .admin_table import load_params_data


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


def update_rights_according_to_params():
    """
    Update the rights table based on the parameters table.

    This function loads the parameters data, extracts the environments, zones, and roles from the data,
    generates all possible combinations of these values, and filters the rights table to keep only the rows
    with combinations found in the generated combinations set. It then finds the missing combinations and adds
    them to the filtered rights table. Finally, it returns the updated rights table.

    Returns:
        pandas.DataFrame: The updated rights table.
    """
    
    df_params = load_params_data()
    envs = df_params[df_params['TYPE'] == 'Env']['SHORT_DESC'].tolist()
    zones = df_params[df_params['TYPE'] == 'Zone']['SHORT_DESC'].tolist()
    roles = df_params[df_params['TYPE'] == 'Role']['SHORT_DESC'].tolist()
    combinations = set(itertools.product(envs, zones, roles))
    df = load_rights_data()
    
    # Filter the DataFrame to keep only rows with combinations found in combinations_set
    df_filtered = df[df.apply(lambda row: (row['ENVIRONMENT'], row['ZONE'], row['ROLE']) in combinations, axis=1)]

    # Find missing combinations and add them
    max_id = df['ID'].max()
    new_rows = []
    
    for combination in combinations:
        if df[(df['ENVIRONMENT'] == combination[0]) & (df['ZONE'] == combination[1]) & (df['ROLE'] == combination[2])].empty:
            max_id += 1  # Update max_id for each new row
            new_rows.append({'ID': max_id, 'ENVIRONMENT': combination[0], 'ZONE': combination[1], 'ROLE': combination[2], 'RIGHTS': '-'})
            
    # Create a DataFrame from new_rows and append it to df_filtered
    if new_rows:
        df_new_rows = pd.DataFrame(new_rows)
        df_filtered = pd.concat([df_filtered, df_new_rows], ignore_index=True)
    return df_filtered
