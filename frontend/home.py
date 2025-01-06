import streamlit as st
import requests
import utils.api_interactions as api
from models import LoginRequest

st.session_state["page"] = None
st.session_state["is_admin"] = False
if "token" not in st.session_state:
    st.session_state["token"] = None

# Handle already logged-in state
if st.session_state["token"]:
    if st.sidebar.button("Translation"):
        st.session_state["page"] = "Translation"
    if st.session_state["is_admin"] and st.sidebar.button("Admin panel"):
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
                    st.success("Login successful! Token stored in session state.")
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
            if reg_password != confirm_password:
                st.error("Passwords do not match!")
            else:
                register_url = "http://host.docker.internal/register"
                try:
                    response = requests.post(
                        register_url,
                        headers={"Content-Type": "application/json"},
                        json={
                            "username": reg_username,
                            "email": reg_email,
                            "password": reg_password,
                        },
                    )

                    if response.status_code == 201:
                        st.success("Registration successful! You can now log in.")
                    else:
                        st.error(f"Registration failed. Status: {response.status_code}, Detail: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")