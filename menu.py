import streamlit as st
import snowflake.connector

def logout():
    if "snow_connector" in st.session_state:
        st.session_state["snow_connector"].close()
        st.success(st.session_state.translations["disconnected"])
        st.session_state.clear()
        st.cache_data.clear()
        st.query_params.clear()


def show_user_and_role():
    # connector = st.session_state.snow_connector
    cur = st.session_state.snow_connector.cursor()
    try:
        user = cur.execute("SELECT CURRENT_USER()").fetchone()[0]
        role = cur.execute("SELECT CURRENT_ROLE()").fetchone()[0]
    except snowflake.connector.errors.ProgrammingError as e:
    # default error message
        st.write(e)
    # customer error message
        st.write('Error {0} ({1}): {2} ({3})'.format(e.errno, e.sqlstate, e.msg, e.sfqid))
    finally:
        cur.close()
    with st.sidebar:
        st.divider()
        st.write("❄️")
        st.write(st.session_state.translations["show_user"] + user)
        st.write(st.session_state.translations["show_role"] + role)
        st.button(st.session_state.translations["logout"], on_click=logout)


def authenticated_menu():
    # Show a navigation menu for authenticated users

    st.sidebar.page_link(
        "pages/1_users.py", label=st.session_state.translations["users"]
    )
    st.sidebar.page_link(
        "pages/2_roles.py", label=st.session_state.translations["roles"]
    )
    st.sidebar.page_link(
        "pages/3_databases.py", label=st.session_state.translations["databases"]
    )
    st.sidebar.page_link(
        "pages/4_list_of_projects.py",
        label=st.session_state.translations["projects_list"],
    )

    show_user_and_role()


def unauthenticated_menu():
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("home.py", label="Home")


def menu():
    # Determine if a user is logged in or not, then show the correct
    # navigation menu

    if "snow_connector" not in st.session_state:
        unauthenticated_menu()
        return
    authenticated_menu()


def menu_with_redirect():
    # Redirect users to the main page if not logged in, otherwise continue to
    # render the navigation menu
    if "snow_connector" not in st.session_state:
        st.switch_page("home.py")
    menu()
