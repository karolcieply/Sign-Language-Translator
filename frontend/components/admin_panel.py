# components/admin_panel.py
import streamlit as st

st.title("Admin Panel")

# Same pattern: check login
if "token" not in st.session_state or not st.session_state["token"]:
    st.error("You are not logged in. Please log in first.")
    st.stop()

st.write("Welcome to the Admin Panel!")
# Optionally add admin-only operations
# for example, a list of users, system stats, etc.
