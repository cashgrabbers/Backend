from fastapi import APIRouter, Depends
from ..utils import get_paypal_session

import requests

from ..dependencies import poll_for_paypal_session

router = APIRouter(
    prefix="/withdraws",
    tags=["withdraws"],
    dependencies=[Depends(poll_for_paypal_session)],
    responses={404: {"description": "Not found"}},
)

fake_withdraws_db = {"plumbus": {"name": "Plumbus"}, "gun": {"name": "Portal Gun"}}

# Define a route to access the retrieved API key
@router.get("/test_get_api_key")
def get_retrieved_api_key():
    return get_paypal_session()
    # return {"retrieved_api_key": getattr(router.state, "session_key", "Not available")}
