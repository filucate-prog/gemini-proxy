import streamlit as st
import requests
from streamlit.web.server.websocket_headers import _get_websocket_headers

st.set_page_config(page_title="Gemini Proxy", layout="centered")

st.title("Gemini Proxy API")

query_params = st.experimental_get_query_params()
url = query_params.get("url", [None])[0]

if not url:
    st.warning("Utilisation : ?url=https://gemini.google.com/share/...")
    st.stop()

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}

try:
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()

    st.json({
        "source": url,
        "raw_html": r.text
    })

except Exception as e:
    st.error(str(e))
