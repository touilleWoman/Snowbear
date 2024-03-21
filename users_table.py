import pandas as pd
import snowflake.connector
import streamlit as st


@st.cache_data
def load_user_data():
    cur = st.session_state.snow_connector.cursor()
    try:
        cur.execute("SHOW USERS")

        cur.execute(
            """
            select "name", "login_name", "first_name", "last_name", "email"
            from table(result_scan(last_query_id())) order by "name"
            """
        )
        df = cur.fetch_pandas_all()
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


def show_df():
    """
    if user search for a user, then show filtered dataframe + selected users
    else show the original dataframe with selected users
    """

    if "df_view" not in st.session_state:
        # To do later : check if user reload when I clear cache
        st.session_state.df_view = load_user_data()
    if "last_search" not in st.session_state:
        st.session_state.last_search = ""
    if "df_buffer" not in st.session_state:
        st.session_state.df_buffer = load_user_data()

    text_search = st.text_input("🔍")

    # use a filter
    if text_search and text_search != st.session_state.last_search:
        df = st.session_state.df_buffer.copy(deep=True)
        selected_rows = df[df["Action"]]
        # take off selected rows from the dataframe
        df = df.drop(selected_rows.index)

        df = filter_df(df, text_search)
        # combine selected rows with the filtered dataframe
        df = pd.concat([df, selected_rows])
        st.session_state.df_view = df

    # delete the filter
    if not text_search and st.session_state.last_search:
        st.session_state.df_view = st.session_state.df_buffer.copy(deep=True)

    st.session_state.last_search = text_search

    st.data_editor(
        st.session_state.df_view,
        key="users_modifs",
        column_config={"name": "user name"},
        on_change=save_selection_in_buffer,
    )


def user_selected():
    st.session_state.one_user_selected = True


class UsersTable:
    def __init__(self) -> None:
        self.cur = st.session_state.snow_connector.cursor()
        self.df = load_user_data()

    def filter_table(self, text_search):
        df = self.df
        m1 = df["name"].str.contains(text_search, case=False)
        m2 = df["login_name"].str.contains(text_search, case=False)
        m3 = df["first_name"].str.contains(text_search, case=False)
        m4 = df["last_name"].str.contains(text_search, case=False)
        m5 = df["email"].str.contains(text_search, case=False)
        filtered_df = df[m1 | m2 | m3 | m4 | m5]
        return filtered_df

    def show_table(self):
        text_search = st.text_input("🔍")
        if text_search:
            filtered_df = self.filter_table(text_search)
            show = filtered_df
            selected_row = self.df[self.df["Action"]]
            st.write(selected_row)
        else:
            show = self.df

        # selected = self.df[self.df["Action"]]

        self.df = st.data_editor(
            show, key="users_list", column_config={"name": "user name"}, hide_index=True
        )

    def active_buttons(self):
        self.show_delete_btton = True

    def new_user(self, login, first_name, last_name, password):
        try:
            self.cur.execute(
                f"""CREATE USER "{login}" PASSWORD="{password}" FIRST_NAME="{first_name}" LAST_NAME="{last_name}"
                """
            )
        except snowflake.connector.errors.ProgrammingError as e:
            st.error(e)
        except Exception as e:
            st.warning(e)
        else:
            st.success(self.cur.fetchone()[0])
            load_user_data.clear()
        finally:
            self.cur.close()

    def delete_user(self):
        selected_rows = self.df[self.df.iloc[:, 3]]
        for _index, row in selected_rows.iterrows():
            name, first_name, last_name, _selection = row
            st.warning(f"Do you confirm the deletion of {first_name} {last_name}")
            if st.button("Confirm", type="primary"):
                cur = st.session_state.snow_connector.cursor()
                try:
                    cur.execute(f"DROP USER {name}")
                except snowflake.connector.errors.ProgrammingError as e:
                    st.write(e)
                except Exception as e:
                    st.warning(e)
                else:
                    st.success(cur.fetchone()[0])
                    load_user_data.clear()
                    st.rerun()
                finally:
                    cur.close()

    def modify_user(self):
        selected_rows = self.df[self.df.iloc[:, 3]]
        if len(selected_rows) != 1:
            st.error("Select ONE user only, Please recheck your selection")
        else:
            name, first, last, _ = selected_rows.values[0]

            change_password = st.toggle(
                f"I want to change user {first} {last}'S password"
            )

            with st.form("modify_user"):
                st.text_input("login", value=name, disabled=True)
                m_first_name = st.text_input("First name", value=first)
                m_last_name = st.text_input("last name", value=last)
                if change_password:
                    password1 = st.text_input("new password", type="password")
                    password2 = st.text_input(
                        "confirm password", type="password", disabled=True
                    )

                # password2 = st.text_input("Confirm password", type="password")
                # if password1 != password2:
                #     st.error("Passwords do not match. Please try again.")
                submitted = st.form_submit_button("Submit", type="primary")
                if submitted:
                    pass
