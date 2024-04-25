import streamlit as st

from menu import menu_with_redirection
from utils.rights_table import load_rights_data

st.set_page_config(page_title="Environments", layout="wide", initial_sidebar_state="auto")
menu_with_redirection()


# when a page is switched, all page related variables are reset, see page.py
page = st.session_state.page
page.switched("rights")

df = load_rights_data()
envs = df["ENVIRONMENT"].unique()

env = st.selectbox("Choose an environment", envs)

filtered_df = df[df["ENVIRONMENT"] == env].drop(columns=["ENVIRONMENT"])


df_view = filtered_df.pivot(index='ROLE', columns='ZONE', values='RIGHTS').fillna('-')

select_box = st.column_config.SelectboxColumn(options=["-", "FULL", "READ", "WRITE", "WRITE/READ"])
df_updated = st.data_editor(df_view, column_order=("BRZ", "SLV", "GLD"), column_config={
    "BRZ": select_box,
    "SLV": select_box,
    "GLD": select_box,
})

if st.button("Submit", type="primary"):
    changes = df_view != df_updated
    # Finding modified rows
    modified_rows = changes.any(axis=1)
    modified_data = df_updated[modified_rows]
    # Applying the highlight function
    # Function to highlight changes
    def highlight_changes(x):
        original = df_view.loc[x.name]
        return ['background-color: yellow' if x[col] != original[col] else '' for col in x.index]
        
    detailed_changes = modified_data.style.apply(highlight_changes, axis=1)
    st.write(detailed_changes)




