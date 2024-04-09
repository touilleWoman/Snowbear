import snowflake.connector
import streamlit as st

from footer import footer
from charge_translations import charge_translations


def logout():
    if "snow_connector" in st.session_state:
        st.session_state["snow_connector"].close()
        st.success(st.session_state.translations["disconnected"])
        st.session_state.clear()
        st.cache_data.clear()
        st.query_params.clear()


@st.cache_data
def get_user():
    cur = st.session_state.snow_connector.cursor()
    try:
        user = cur.execute("SELECT CURRENT_USER()").fetchone()[0]
    except snowflake.connector.errors.ProgrammingError as e:
        # default error message
        st.write(e)
        # customer error message
        st.write(
            "Error {0} ({1}): {2} ({3})".format(e.errno, e.sqlstate, e.msg, e.sfqid)
        )
    finally:
        cur.close()
    return user


def show_user():
    user = get_user()
    with st.sidebar:
        st.divider()
        st.write(f"❄️{user}")
        st.button(st.session_state.translations["logout"], on_click=logout)


def authenticated_menu():
    if "selected_lang" not in st.session_state:
        st.session_state.selected_lang = None

    with st.sidebar:
        # default value will be 'fr' without selection
        selected_lang = st.selectbox("🌐", ["fr", "en"])
        st.divider()

    st.session_state.translations = charge_translations(selected_lang)
    st.session_state.selected_lang = selected_lang

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

    st.sidebar.divider()
    st.sidebar.title("Admin")
    st.sidebar.page_link(
        "pages/5_admin_env.py", label=st.session_state.translations["environments"]
    )
    st.sidebar.page_link("pages/6_admin_zone.py", label="Zones")
    st.sidebar.page_link(
        "pages/7_admin_role.py", label=st.session_state.translations["roles"]
    )
    st.sidebar.page_link(
        "pages/8_admin_rights.py", label=st.session_state.translations["rights"]
    )

    show_user()
    st.sidebar.divider()
    st.sidebar.caption("Powered by")
    st.sidebar.image("./images/logo_hardis.png", use_column_width=True)

    # Show a navigation menu for unauthenticated users
    # st.sidebar.page_link("home.py", label="Home")


def menu_with_redirection():
    # Determine if a user is logged in or not, then show the correct
    # navigation menu

    if "snow_connector" not in st.session_state:
        st.switch_page("home.py")
    else:
        authenticated_menu()
        footer()


if __name__ == "__main__":
    menu_with_redirection()
