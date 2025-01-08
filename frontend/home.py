import time

import streamlit as st
import utils.api_interactions as api
from models import LoginRequest, UserRequest, RegisterUserRequest

if "page" not in st.session_state:
    st.session_state["page"] = None
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False
if "token" not in st.session_state:
    st.session_state["token"] = None

# Handle already logged-in state
if st.session_state["token"]:
    if st.sidebar.button("Translation"):
        st.session_state["page"] = "Translation"
    if st.session_state["is_admin"]:
        button = st.sidebar.button("Admin panel")
        if button:
            st.session_state["page"] = "Admin panel"
    if st.sidebar.button("Logout"):
        st.session_state["token"] = None
        st.session_state["page"] = None
        st.rerun()

    if st.session_state.get("page") == "Translation" or st.session_state["page"] is None:
        exec(open("frontend/components/translator.py").read())
    elif st.session_state.get("page") == "Admin panel":
        exec(open("frontend/components/admin_panel.py").read())
else:
    tab1, tab2 = st.tabs(["Log In", "Register"])

    with tab1:
        st.subheader("Log In")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            login_request = LoginRequest(username=login_username, password=login_password)
            try:
                response = api.api_login(login_request)
                if isinstance(response, dict) and "error" in response:
                    st.error(response["error"])
                else:
                    st.session_state["token"] = response.access_token
                    st.session_state["is_admin"] = response.is_admin
                    st.session_state["user_id"] = response.user_id
                    st.success("Login successful! Token stored in session state.")
                    st.write(f"st.session_state: {st.session_state}")
                    time.sleep(2)
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

    with tab2:
        st.subheader("Register")
        reg_username = st.text_input("Username", key="reg_username")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        confirm_password = st.text_input("Confirm Password", type="password", key="confirm_password")

        if st.button("Register"):
            if len(reg_password) < 8 or not any(char.isdigit() for char in reg_password) or not any(char.isalpha() for char in reg_password):
                st.error("Password must be at least 8 characters long and contain at least one letter and one digit.")
            elif reg_password != confirm_password:
                st.error("Passwords do not match!")
            elif "@" not in reg_email or "." not in reg_email:
                st.error("Invalid email address!")
            else:
                register_request = RegisterUserRequest(username=reg_username, email=reg_email, password=reg_password)
                try:
                    response = api.api_register(register_request)
                    if "error" in response:
                        st.error(response["error"])
                    else:
                        st.session_state["token"] = response.access_token
                        st.session_state["is_admin"] = response.is_admin
                        st.session_state["user_id"] = response.user_id
                        st.success("Registration successful!")
                        time.sleep(2)
                        st.write(f"st.session_state: {st.session_state}")
                        st.rerun()
                except Exception as e:
                    st.error(f"Error: {e}")
