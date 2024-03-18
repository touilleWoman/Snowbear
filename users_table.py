import snowflake.connector
import streamlit as st
import pandas as pd

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


def update_df_users(df):
    """
    user clicked one selectbox, 
    update the dataframe column 'Action' with the new value(True/False)
    """

    modifs = st.session_state.users_modifs["edited_rows"]
    for index, value in modifs.items():
        df.iloc[index, -1] = value["Action"]
    if len(st.session_state.df_users) == len(df):
        st.session_state.df_users = df
    else:
        for index, row in df.iterrows():
            st.session_state.df_users.loc[st.session_state.df_users['name'] == row['name'],"Action"] = row["Action"]


def show_df():
    """
    if user search for a user, then show filtered dataframe + selected users
    else show the original dataframe with selected users
    """

    
    text_search = st.text_input("🔍")
    df = st.session_state.df_users.copy()

    if text_search:
        selected_rows = df[df["Action"]]
        
        #take off selected rows from the dataframe
        df = df.drop(selected_rows.index)
        
        df = filter_df(df, text_search)
        # combine selected rows with the filtered dataframe
        df = pd.concat([df, selected_rows])

    st.data_editor(
        df,
        key="users_modifs",
        column_config={"name": "user name"},
        on_change=update_df_users,
        args=[df],
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
