# Snowflake OAuth2 Configuration for Streamlit App

## Overview

This README provides instructions on how to configure Snowflake OAuth2 integration for a Streamlit application. Snowflake OAuth2 integration allows users to authenticate with Snowflake using OAuth2 and access Snowflake resources securely from within the Streamlit app.


## Snowflake OAuth2 Configuration

Follow these steps to configure Snowflake OAuth2 integration for your Streamlit application:

1. **Create OAuth2 Integration in Snowflake**:
   
   Log in to your Snowflake account and create an OAuth2 integration object using the following SQL command:
   
   ```sql
    CREATE OR REPLACE SECURITY INTEGRATION <integration_name>
    TYPE=OAUTH
    ENABLED=TRUE
    OAUTH_ALLOW_NON_TLS_REDIRECT_URI = TRUE
    OAUTH_CLIENT = CUSTOM
    OAUTH_CLIENT_TYPE='CONFIDENTIAL'
    OAUTH_REDIRECT_URI='http://localhost:8501'
    OAUTH_ISSUE_REFRESH_TOKENS = TRUE
    OAUTH_REFRESH_TOKEN_VALIDITY = 86400
    ;

2. **Grant Privileges**:


   Grant privileges to the OAuth2 integration object for the Snowflake role that will be used to access Snowflake resources from the Streamlit application. For example:

    ```sql
    GRANT USAGE ON INTEGRATION <integration_name> TO ROLE <role_name>;

3. **Configure Streamlit App:**


   In your Streamlit application code, provide the Snowflake OAuth2 configuration details, generated with the commande sql in step1,including the OAuth2 client ID, client secret, authorization endpoint, token endpoint, and redirect URI. Ensure that this information is securely stored and retrieved within your Streamlit app. You can use Streamlit secrets(~/.streamlit/secrets.toml) for this purpose.
   It should be something look like this:
```
   [snowauth]
    account = "<ACCOUNTID>.west-europe.azure"
    authorization_endpoint = "https://<ACCOUNTID>.snowflakecomputing.com/oauth/authorize"
    token_endpoint = "https://<ACCOUNTID>.snowflakecomputing.com/oauth/token-request"
    redirect_uri = 'http://localhost:8501'
    client_id = "<OAUTH CLIENT ID>"
    client_secret = "<OAUTH CLIENT SECRET>"
    role = "<SNOWFLAKE ROLE>"
```




