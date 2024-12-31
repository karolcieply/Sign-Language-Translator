"""Main Streamlit application file."""

import streamlit as st

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def login() -> None:
    """Log in the user."""
    if st.button("Log in"):
        st.session_state.logged_in = True
        st.rerun()


def logout() -> None:
    """Log out the user."""
    if st.button("Log out"):
        st.session_state.logged_in = False
        st.rerun()


login_page = st.Page(login, title="Log in", icon=":material/login:")
logout_page = st.Page(logout, title="Log out", icon=":material/logout:")


pg = st.navigation({"Account": [logout_page]}) if st.session_state.logged_in else st.navigation([login_page])

pg.run()
