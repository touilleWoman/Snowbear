import streamlit as st
from streamlit_cookies_manager import EncryptedCookieManager

def select_lang():
    # This should be on top of your script
    cookies = EncryptedCookieManager(
        # This prefix will get added to all your cookie names.
        # This way you can run your app on Streamlit Cloud without cookie name clashes with other apps.
        prefix="ktosiek/streamlit-cookies-manager/",
        # You should really setup a long COOKIES_PASSWORD secret if you're running on Streamlit Cloud.
        password="My secret password"
    )
    if not cookies.ready():
        # Wait for the component to load and send us current cookies.
        st.stop()


    # default value will be 'fr' without selection
    lang_in_cookies = cookies["language"]

    if lang_in_cookies == 'en':
        lang_list = ["en", "fr"]
    else :
        lang_list = ["fr", "en"]
    selected_lang = st.selectbox("🌐", lang_list)
    cookies['language'] = selected_lang  # This will get saved on next rerun
    cookies.save()  # Force saving the cookies now, without a rerun