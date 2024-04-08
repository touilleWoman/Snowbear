import streamlit as st
import snowflake.connector
from charge_translations import charge_translations
from snow_oauth import SnowOauth
from footer import footer
from utils.admin_table import get_types


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


def authenticated_menu(show_admin_radio):
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
    st.sidebar.page_link("pages/5_admin.py", label="Admin")
    if show_admin_radio:
        # Initialize st.session_state.type
        st.session_state.type = st.sidebar.radio(
            "types",
            get_types(),
            label_visibility="hidden",
        )
    show_user()
    st.sidebar.divider()
    st.sidebar.caption("Powered by")
    st.sidebar.image("./images/logo_hardis.png", use_column_width=True)


def unauthenticated_menu():
    col_hardis, col_partner = st.columns([1, 6])
    with col_hardis:
        st.image("./images/logo_hardis.png", width=200)
    with col_partner:
        st.image("./images/place_holder.jpg", width=200)

    st.header("❄️ Welcome to your SNOW BEAR ❄️")
    st.header("❄️ Bienvenue à votre SNOW BEAR ❄️")
    oauth = SnowOauth(label="Se connecter à Snowflake")
    oauth.start_session()
    # Show a navigation menu for unauthenticated users
    st.sidebar.page_link("home.py", label="Home")


def menu(show_admin_radio=False):
    # Determine if a user is logged in or not, then show the correct
    # navigation menu

    if "snow_connector" not in st.session_state:
        unauthenticated_menu()
    else:
        authenticated_menu(show_admin_radio)
    footer()


def menu_with_redirect():
    # Redirect users to the main page if not logged in, otherwise continue to
    # render the navigation menu
    if "snow_connector" not in st.session_state:
        st.switch_page("home.py")
    menu()


if __name__ == "__main__":
    menu()
