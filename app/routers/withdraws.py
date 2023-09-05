from fastapi import APIRouter, Depends, HTTPException

from ..config import settings
import requests

from ..dependencies import poll_for_paypal_session

router = APIRouter(
    prefix="/withdraws",
    tags=["withdraws"],
    dependencies=[Depends(poll_for_paypal_session)],
    responses={404: {"description": "Not found"}},
)

fake_withdraws_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}


def get_paypal_session():
    try:
        url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

        payload = 'grant_type=client_credentials'
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic '+ settings.PAYPAL_API_KEY,
        }
        response = requests.request("POST", url, headers=headers, data=payload)

        response.raise_for_status()  # Raise an exception for non-2xx responses
        access_token = response.json().get("access_token")

        return access_token
    
    except Exception as e:
        # Handle exceptions as needed
        pass


# Define a route to access the retrieved API key
@router.get("/test_get_api_key")
def get_retrieved_api_key():
    return get_paypal_session()
    # return {"retrieved_api_key": getattr(router.state, "session_key", "Not available")}
