import streamlit as st

from menu import menu_with_redirection
from utils.rights_table import (
    sync_rights_table_with_params,
    update_modified_rights_table,
)
from utils.admin_table import load_params_data

st.set_page_config(
    page_title="Environments", layout="wide", initial_sidebar_state="auto"
)
menu_with_redirection()


# when a page is switched, all page related variables are reset, see page.py
page = st.session_state.page
page.switched("admin_rights")

df = sync_rights_table_with_params()

df_params = load_params_data()
envs = (
    df_params[df_params["TYPE"] == "Env"].sort_values(by="ORDER")["SHORT_DESC"].tolist()
)

first_container = st.container(border=True)
with first_container:
    env = st.selectbox("Choose an environment", envs)

filtered_df = df[df["ENVIRONMENT"] == env].drop(columns=["ENVIRONMENT"])


df_view = filtered_df.pivot(index="ROLE", columns="ZONE", values="RIGHTS").fillna("-")

# Reorder columns based on the desired order, but filter out any that don't exist in the current DataFrame
desired_order = ["BRZ", "SLV", "GLD"]
ordered_columns = [col for col in desired_order if col in df_view.columns]
df_view = df_view.reindex(columns=ordered_columns)

selected = st.column_config.SelectboxColumn(
    default=0, options=["-", "FULL", "READ", "WRITE", "WRITE/READ"]
)
column_config = {column: selected for column in df_view.columns}

with first_container:
    df_updated = st.data_editor(df_view, column_config=column_config)
    st.button(
        st.session_state.transl["modify"],
        type="primary",
        disabled=page.disabled["modify"],
        on_click=page.switch_button,
        args=["modify"],
    )

second_container = st.container(border=True)
with second_container:
    if page.clicks["modify"]:
        changes = df_view != df_updated
        # Finding modified rows
        modified_rows = changes.any(axis=1)
        modified_data = df_updated[modified_rows]

        # Applying the highlight function
        def highlight_changes(x):
            original = df_view.loc[x.name]
            return [
                "background-color: yellow" if x[col] != original[col] else ""
                for col in x.index
            ]

        detailed_changes = modified_data.style.apply(highlight_changes, axis=1)
        st.write(detailed_changes)

        modif_confirmed = st.button("Confirm", key="confirm", type="primary")
        if modif_confirmed:
            # Extract the changes and display
            changes_list = []
            for idx, row in modified_data.iterrows():
                for col in row.index:
                    original_value = df_view.loc[idx, col]
                    new_value = df_updated.loc[idx, col]
                    if original_value != new_value:
                        changes_list.append(
                            {
                                "Role": idx,
                                "Zone": col,
                                "Value": new_value,
                                "Enviroment": env,
                            }
                        )
            update_modified_rights_table(changes_list)

if page.message:
    for msg in page.message:
        if "Error" in msg:
            st.toast(f":red[{msg}]", icon="❌")
        else:
            st.toast(f":green[{msg}]", icon="✅")
    page.message = []
