import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from snowflake.snowpark import Session

_DEFAULT_SECRET_KEY = "snowauth"


def logout():
    if "snowpark_session" in st.session_state:
        st.session_state["snowpark_session"].close()
        for key in st.session_state.keys():
            del st.session_state[key]
        st.query_params.pop("code")
        st.query_params.pop("state")


def validate_config(config):
    required_config_options = [
        "authorization_endpoint",
        "token_endpoint",
        "redirect_uri",
        "client_id",
        "client_secret",
        "account",
    ]
    return all([k in config for k in required_config_options])


def login_snowflake(config, label):
    if "authorization_url" not in st.session_state:
        oauth = OAuth2Session(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            redirect_uri=config["redirect_uri"],
            role=config["role"],
        )
        authorization_url, expected_state = oauth.create_authorization_url(
            config["authorization_endpoint"]
        )
        st.session_state.authorization_url = authorization_url
    # !!! st.session_state will be cleared out when this button get clicked(page redirection)
    st.link_button(label, url=st.session_state.authorization_url, type="primary")

    # st.session_state.expected_state = expected_state


def get_access_token(label, config, auth_code):
    token_url = config["token_endpoint"]
    client_id = config["client_id"]
    client_secret = config["client_secret"]
    redirect_uri = config["redirect_uri"]

    oauth = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri)
    try:
        token = oauth.fetch_token(token_url, code=auth_code)
    except Exception as e:
        st.error(e)
        st.stop()
    return token


def snowauth_session(config=None, label="Login to Snowflake"):
    """
    Authenticate and start a Snowpark session in Streamlit.

    This function initiates the OAuth2 authentication flow for Snowflake and starts a Snowflake session
    in Streamlit based on the provided configuration.

    Args:
    - config (dict, optional): Snowflake OAuth2 configuration dictionary or the name of the secret to
      retrieve the configuration from Streamlit secrets. If not provided, the default configuration(in ~/.streamlit/secrets.toml) is used.
    - label (str, optional): Label for the login button. Default is "Login to Snowflake".

    Returns: None ; the snowpark session generated is stored in streamlit: st.session_state.snowpark_session

    """

    # if not config, use default config in ~/.streamlit/secrets.toml
    if not config:
        config = _DEFAULT_SECRET_KEY
    if isinstance(config, str):
        config = st.secrets[config]
    if not validate_config(config):
        st.error("Invalid OAuth Configuration")
        st.stop()

    if "code" not in st.query_params.keys():
        login_snowflake(config, label)
    else:
        auth_code = st.query_params.get("code")
        returned_state = st.query_params.get("state")
        print(f"returned state{returned_state}")
        # if returned_state != st.session_state.expected_state:
        #     st.error("CSRF Error: State mismatch. This may be a security threat.")
        #     st.stop()

        token = get_access_token(label, config, auth_code)

        snow_configs = {
            "account": config["account"],
            "authenticator": "oauth",
            "token": token["access_token"],
        }
        try:
            st.session_state["snowpark_session"] = Session.builder.configs(
                snow_configs
            ).create()
            st.success("Snowpark session start now !")
            st.sidebar.button("Logout", on_click=logout)
        except Exception as e:
            st.error(f"Error connecting to Snowflake: \n{str(e)}")
            login_snowflake(config, label)
