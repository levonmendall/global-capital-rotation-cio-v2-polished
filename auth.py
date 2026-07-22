
import os, hmac
import streamlit as st

def require_login():
    expected = os.getenv("APP_PASSWORD", "").strip()
    if not expected:
        return
    if st.session_state.get("authenticated"):
        return
    st.markdown("<div style='height:10vh'></div>", unsafe_allow_html=True)
    st.title("Global Capital Rotation CIO")
    st.caption("Private V2 access")
    entered = st.text_input("Password", type="password")
    if st.button("Sign in", type="primary", use_container_width=True):
        if hmac.compare_digest(entered, expected):
            st.session_state.authenticated = True
            st.rerun()
        st.error("Incorrect password.")
    st.stop()
