import pandas as pd
import streamlit as st


@st.cache_data
def load_user_data():
    cur = st.session_state.snow_connector.cursor()
    try:
        cur.execute("SHOW USERS")
        df = pd.DataFrame(cur.fetchall(), columns=[desc[0] for desc in cur.description])
        selected_columns = [
            "name",
            "login_name",
            "first_name",
            "last_name",
            "email",
            "disabled",
        ]
        df = df[selected_columns]
        df["Action"] = False

    except Exception as e:
        st.error(e)
    finally:
        cur.close()
    return df


def filter_df(df, text_search):
    m1 = df["name"].str.contains(text_search, case=False)
    m2 = df["login_name"].str.contains(text_search, case=False)
    m3 = df["first_name"].str.contains(text_search, case=False)
    m4 = df["last_name"].str.contains(text_search, case=False)
    m5 = df["email"].str.contains(text_search, case=False)
    filtered_df = df[m1 | m2 | m3 | m4 | m5]
    return filtered_df


def update_nb_selected_in_session_state():
    """
    check if the user selected at least one user
    """

    df = st.session_state.df_buffer
    st.session_state.nb_selected = len(df[df["Action"]])


def save_selection_in_buffer():
    """
    user clicked one selectbox,
    in dataframe: st.session_state.df_buffer
    update the column 'Action' with the new value(True/False)
    """

    df = st.session_state.df_view.copy(deep=True)
    modifs = st.session_state.users_modifs["edited_rows"]
    for index, value in modifs.items():
        df.iloc[index, -1] = value["Action"]
        name = df.iloc[index]["name"]
        st.session_state.df_buffer.loc[
            st.session_state.df_buffer["name"] == name, "Action"
        ] = value["Action"]
    update_nb_selected_in_session_state()


def main_interaction():
    """
    if user search for a user, then show filtered dataframe + selected users
    else show the original dataframe with selected users

    !!!important information:
    - df_view is the dataframe that the user see
    - df_buffer is the dataframe which store the selections
    why this complexity? because streamlit has a specific way to handle dataframes
    each time we click on a selectbox, the application rerun from the top, but on the front end
    it doesn't always reload the dataframe to avoid flashing effect,
    it will reload when the parameters of st.data_editor change.
    So If we change the value of df_view each time we click, the page will flash each time we click.
    To avoid this, we use df_buffer to store the selections,
    and we update the df_view only when we use the filter or when we take off the filer

    """

    if "df_view" not in st.session_state:
        st.session_state.df_view = load_user_data()
        st.session_state.df_buffer = load_user_data()

    if "last_search" not in st.session_state:
        st.session_state.last_search = ""

    text_search = st.text_input("🔍")

    # use a filter
    if text_search and text_search != st.session_state.last_search:
        df = st.session_state.df_buffer.copy(deep=True)
        selected_rows = df[df["Action"]]

        # take off selected rows from the dataframe to avoid duplicates
        df = df.drop(selected_rows.index)

        df = filter_df(df, text_search)

        # combine selected rows with the filtered dataframe
        df = pd.concat([df, selected_rows])

        # update the view
        st.session_state.df_view = df

    # delete the filter, so update the view
    if not text_search and st.session_state.last_search:
        st.session_state.df_view = st.session_state.df_buffer.copy(deep=True)

    st.session_state.last_search = text_search

    st.data_editor(
        st.session_state.df_view,
        key="users_modifs",
        column_config={
            "name": "User name",
            "login_name": "Login name",
            "first_name": st.session_state.transl["first_name"],
            "last_name": st.session_state.transl["last_name"],
            "disabled": st.session_state.transl["disabled"],
            "email": "Email",
        },
        on_change=save_selection_in_buffer,
    )
