import snowflake.connector
import streamlit as st
from pandas import DataFrame





@st.cache_data
def load_user_data():
    cur = st.session_state.snow_connector.cursor()
    try:
        cur.execute(
            # "SELECT LOGIN_NAME, FIRST_NAME, LAST_NAME FROM snowflake.account_usage.users;"
            "SHOW USERS"
        )
        cur.execute(
            """
            select "login_name", "first_name", "last_name", "email"
            from table(result_scan(last_query_id())) order by "login_name"
            """
        )
        df = DataFrame(cur.fetchall())
        breakpoint()
        df[3] = False

    except Exception as e:
        st.error(e)
    finally:
        cur.close()
    
    return df

def user_selected():
    st.session_state.one_user_selected = True

class UsersTable:
    def __init__(self) -> None:
        self.cur = st.session_state.snow_connector.cursor()
        self.show_delete_button = False
        self.show_modify_button = False
        self.delete_button_clicked = False

        try:
            df = load_user_data()
            self.df = st.data_editor(
                df,
                column_config={
                    "0": "login",
                    "1": "first name",
                    "2": "last name",
                    "3": st.column_config.CheckboxColumn(
                        "Action", help="Select to modify or delete user", default=False
                    ),
                },
                hide_index=True,
                on_change=self.active_buttons 
                # on_change=user_selected
                )
        except Exception as e:
            # test excpetion here !!!!
            st.write(e)
            raise Exception(e)

    def active_buttons(self):
        self.show_delete_btton = True

    def new_user(self, login, first_name, last_name, password):
        try:
            self.cur.execute(f"""CREATE USER "{login}" PASSWORD="{password}" FIRST_NAME="{first_name}" LAST_NAME="{last_name}"
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
            
            change_password = st.toggle(f"I want to change user {first} {last}'S password")
                
            with st.form("modify_user"):
                st.text_input("login", value = name, disabled=True)
                m_first_name = st.text_input("First name", value=first)
                m_last_name = st.text_input("last name", value=last)
                if change_password:
                    password1 = st.text_input("new password", type="password")
                    password2 = st.text_input("confirm password", type="password", disabled=True)

                # password2 = st.text_input("Confirm password", type="password")
                # if password1 != password2:
                #     st.error("Passwords do not match. Please try again.")
                submitted = st.form_submit_button("Submit", type="primary")
                if submitted:
                    pass