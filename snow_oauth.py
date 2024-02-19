import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from snowflake.snowpark import Session


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


class SnowOauth:
    """
    A class for authenticating with Snowflake using OAuth2 and starting a Snowpark session in Streamlit.

    This class provides methods to initiate the OAuth2 authentication flow for Snowflake,
    obtain access tokens, and start a Snowpark session in Streamlit based on the provided configuration.

    Attributes:
    - label (str): Label for the login button. Default is "Login to Snowflake".
    - config (dict): Snowflake OAuth2 configuration dictionary.

    Main Methods:
    - start_session: Initiates the authentication flow and starts a Snowpark session in Streamlit.

    Usage:
    ```
    snow_oauth = SnowOauth(label="Login to Snowflake", config=my_config)
    snow_oauth.start_session()
    ```
    !!!the snowpark session generated is stored in streamlit: st.session_state.snowpark_session

    """
    def __init__(self, label="Login to Snowflake", config=None) -> None:
        """
        Initializes a SnowOauth instance with the specified label and configuration.

        Args:
        - label (str, optional): Label for the login button. Default is "Login to Snowflake".
        - config (dict, optional): Snowflake OAuth2 configuration dictionary.
          If not provided, the default configuration (in ~/.streamlit/secrets.toml) is used.

        """
        if not config:
            config = st.secrets["snowauth"]
        if not validate_config(config):
            raise ValueError("Invalid OAuth Configuration")

        self.config = config
        self.label = label

    def start_session(self):
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

        if "code" not in st.query_params.keys():
            self.login_snowflake()
        else:
            auth_code = st.query_params.get("code")
            returned_state = st.query_params.get("state")
            print(f"returned state{returned_state}")
            # if returned_state != st.session_state.expected_state:
            #     st.error("CSRF Error: State mismatch. This may be a security threat.")
            #     st.stop()

            token = self.get_access_token(auth_code)

            snow_configs = {
                "account": self.config["account"],
                "authenticator": "oauth",
                "token": token["access_token"],
            }
            try:
                st.session_state["snowpark_session"] = Session.builder.configs(
                    snow_configs
                ).create()
                st.success("Snowpark session start now !")
                st.write(st.session_state.snowpark_session)
                st.rerun()
            except Exception as e:
                st.error(f"Error connecting to Snowflake: \n{str(e)}")

    def login_snowflake(self):
        """
        Generates the authorization URL and displays the login button in Streamlit.

        """

        if "authorization_url" not in st.session_state:
            oauth = OAuth2Session(
                client_id=self.config["client_id"],
                client_secret=self.config["client_secret"],
                redirect_uri=self.config["redirect_uri"],
                role=self.config["role"],
            )
            authorization_url, expected_state = oauth.create_authorization_url(
                self.config["authorization_endpoint"]
            )
            st.session_state.authorization_url = authorization_url
        # !!! st.session_state will be cleared out when this button get clicked(page redirection)
        st.link_button(
            self.label, url=st.session_state.authorization_url, type="primary"
        )

        # st.session_state.expected_state = expected_state

    def get_access_token(self, auth_code):
        """
        Retrieves the access token using the authorization code obtained from Snowflake.

        Args:
        - auth_code (str): Authorization code obtained from Snowflake.

        Returns:
        - token (dict): Access token dictionary containing token information.

        """

        token_url = self.config["token_endpoint"]
        client_id = self.config["client_id"]
        client_secret = self.config["client_secret"]
        redirect_uri = self.config["redirect_uri"]

        oauth = OAuth2Session(client_id, client_secret, redirect_uri=redirect_uri)
        try:
            token = oauth.fetch_token(token_url, code=auth_code)
        except Exception as e:
            st.error(e)
            st.stop()
        return token
