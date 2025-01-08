import os
from http import HTTPStatus
import streamlit as st

import requests
from pydantic import ValidationError

from frontend.models import UserRequest, LoginRequest, LoginResponse, FrontendSettings, RegisterUserRequest

settings = FrontendSettings()
backend_url = settings.backend_server
def api_login(request_data: LoginRequest) -> LoginResponse | dict:
    """Log in user and return access token and admin status.

    Args:
        request_data: LoginRequest object with username and password.

    Returns:
        LoginResponse: LoginResponse object with access token and admin status.
    """
    try:
        with requests.post(
            url=f"http://{backend_url}/auth/login",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=request_data.dict(),
            timeout=10,
        ) as response:
            if response.status_code == HTTPStatus.OK:
                try:
                    return LoginResponse(**response.json())
                except ValidationError as e:
                    msg = f"Invalid response format: {e}"
                    raise ValidationError(msg) from e
            elif response.status_code == HTTPStatus.UNAUTHORIZED:
                return {"error": "Invalid username or password."}
            else:
                response.raise_for_status()
    except requests.RequestException as e:
        msg = f"Login request failed: {e}"
        raise requests.HTTPError(msg) from e


def api_register(request_data: RegisterUserRequest) -> LoginResponse | dict:
    """Register a new user.

    Args:
        request_data: UserRequest object with username, email, and password.

    Returns:
        dict: Response message.
    """
    try:
        st.write(f"{request_data.dict()}")
        with requests.post(
            url=f"http://{backend_url}/auth/register",
            headers={"Content-Type": "application/json"},
            json=request_data.dict(),
            timeout=10,
        ) as response:
            if response.status_code == HTTPStatus.OK:
                return LoginResponse(**response.json())
            if response.status_code == HTTPStatus.CONFLICT:
                return {"error": "Username or email already exists."}
            response.raise_for_status()
    except requests.RequestException as e:
        msg = f"Registration request failed: {e}"
        raise requests.HTTPError(msg) from e


def api_get_users() -> list[UserRequest]:
    """Get all users from database.

    Returns:
        list: List of all users.
    """
    try:
        with requests.get(
            url=f"http://{backend_url}/users",
            headers={"Content-Type": "application/json"},
            timeout=10,
        ) as response:
            response.raise_for_status()
            return response.json()
    except requests.RequestException as e:
        msg = f"Get users request failed: {e}"
        raise requests.HTTPError(msg) from e


def api_update_user(request_data: list[UserRequest]) -> True:
    """Update user details.

    Args:
        request_data: UserRequest object with email, is_admin, and user_name and is_active.

    Returns:
        True if the update was successful, False otherwise.
    """
    resp_stat = []
    try:
        for user in request_data:
            response = requests.put(
                url=f"http://{backend_url}/users/{user.id}",
                headers={"Content-Type": "application/json"},
                json=user.dict(exclude={"id"}),
                timeout=10,
            )
            resp_stat.append(response.status_code)
        return all(status == HTTPStatus.OK for status in resp_stat)
    except requests.RequestException as e:
        msg = f"Update user request failed: {e}"
        raise requests.HTTPError(msg) from e
