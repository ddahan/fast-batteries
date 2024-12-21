from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Request, status
from fastapi.responses import RedirectResponse

from app.core.config import get_settings
from app.core.database import SessionDep
from app.models.user import User
from app.schemas.token import AccessJWT

settings = get_settings()

router = APIRouter(prefix="/auth", tags=["Social Auth"])


@router.get("/linkedin", response_model=str)
def linkedin_auth():
    """Build and return the full Linked In authorization URL to redirect to"""

    params = {
        "response_type": "code",
        "client_id": settings.LINKEDIN_CLIENT_ID,
        "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
        "scope": settings.LINKEDIN_SCOPES,
    }
    full_authorization_url = f"{settings.LINKEDIN_AUTHORIZATION_URL}?{urlencode(params)}"
    return full_authorization_url


@router.get("/linkedin/callback")
def linkedin_auth_callback(request: Request, session: SessionDep):
    """Hook called by Linked In during OAuth2 process"""

    def redirect_to_front(token: AccessJWT | None = None, error: str | None = None):
        """Called to redirect properly to front-end when back-end handling is done.
        Contains app access token if successful, and error otherwise."""

        params: dict[str, Any] = {}
        if error:
            params = {"error": error}
        if token:
            params = token.model_dump(by_alias=True)

        query_string = urlencode(params)
        url = settings.SOCIAL_AUTH_FRONT_REDIRECT_URL
        if params:
            url += f"?{query_string}"

        return RedirectResponse(url)

    # After the users grants permission, linked in provides a single-use authorization code
    code = request.query_params.get("code")
    if code is None:
        return redirect_to_front(error="Can't get code in the request query params")

    # Prepare the data to exchange the code for an access token
    data: dict[str, str] = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
        "client_id": settings.LINKEDIN_CLIENT_ID,
        "client_secret": settings.LINKEDIN_CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # Send the request to LinkedIn, and parse the response to get the linked in access token
    with httpx.Client() as client:
        response = client.post(settings.LINKEDIN_TOKEN_URL, data=data, headers=headers)

    if response.status_code != status.HTTP_200_OK:
        return redirect_to_front(
            error="Unable to authenticate with Linked In. Please try again later."
        )

    linkedin_access_token = response.json().get("access_token")
    if not linkedin_access_token:
        return redirect_to_front(error="Access token not found in response")

    # Send the get profile request to LinkedIn, using the access token
    with httpx.Client() as client:
        response = client.get(
            url=settings.LINKEDIN_PROFILE_URL,
            headers={"Authorization": f"Bearer {linkedin_access_token}"},
        )

    if response.status_code != status.HTTP_200_OK:
        return redirect_to_front(error="Failed to fetch LinkedIn profile")

    app_access_token = User.handle_linkedin_profile(
        profile=response.json(), session=session
    )

    if app_access_token is None:
        return redirect_to_front(
            error="There is an existing account with this email, but used with another \
            login method. Please log in again using this method."
        )

    # At this point, the user will be redirect to home page, no matter whether it's
    # a signup or a login, so we don't need more data than the access token.
    return redirect_to_front(token=app_access_token)
