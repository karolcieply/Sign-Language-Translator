import requests
from http import HTTPStatus
from pydantic import ValidationError
from frontend.models import LoginRequest, LoginResponse, CreateUserRequest, UpdateUserRequest


def api_login(request_data: LoginRequest) -> LoginResponse | dict:
    """Log in user and return access token and admin status.

    Args:
        request_data: LoginRequest object with username and password.

    Returns:
        LoginResponse: LoginResponse object with access token and admin status.
    """
    try:
        with requests.post(
            url="http://host.docker.internal/login",
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


def api_register(request_data: CreateUserRequest) -> dict:
    """Register a new user.

    Args:
        request_data: CreateUserRequest object with username, email, and password.

    Returns:
        dict: Response message.
    """
    try:
        with requests.post(
            url="http://host.docker.internal/register",
            headers={"Content-Type": "application/json"},
            json=request_data.dict(),
            timeout=10,
        ) as response:
            if response.status_code == HTTPStatus.CREATED:
                return {"message": "User created successfully."}
            elif response.status_code == HTTPStatus.CONFLICT:
                return {"error": "Username or email already exists."}
            else:
                response.raise_for_status()
    except requests.RequestException as e:
        msg = f"Registration request failed: {e}"
        raise requests.HTTPError(msg) from e


def api_update_user(request_data: UpdateUserRequest) -> dict:
    """Update user details.

    Args:
        request_data: UpdateUserRequest object with email, is_admin, and user_name.

    Returns:
        dict: Response message.
    """
    try:
        with requests.put(
            url="http://host.docker.internal/update_user",
            headers={"Content-Type": "application/json"},
            json=request_data.dict(),
            timeout=10,
        ) as response:
            if response.status_code == HTTPStatus.OK:
                return {"message": "User updated successfully."}
            elif response.status_code == HTTPStatus.NOT_FOUND:
                return {"error": "User not found."}
            else:
                response.raise_for_status()
    except requests.RequestException as e:
        msg = f"Update user request failed: {e}"
        raise requests.HTTPError(msg) from e


