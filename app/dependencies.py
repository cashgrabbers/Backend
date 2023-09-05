
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.config import settings

# Function to poll for the API key
def poll_for_paypal_session():
    try:
        url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

        payload = 'grant_type=client_credentials'
        headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic '+ settings.PAYPAL_API_KEY,
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()  # Raise an exception for non-2xx responses
        data = response.json()
        api_key = data.get("access_token")
        if api_key:
            # Store the retrieved API key securely, e.g., in a database or environment variable
            # This is just a placeholder example
            # app.state.api_key = api_key
            pass
    except Exception as e:
        # Handle exceptions as needed
        pass

# Function to run the background task for polling the API key
def run_polling_task():
    scheduler = BackgroundScheduler()
    # Schedule the task to run every hour (adjust as needed)
    scheduler.add_job(poll_for_paypal_session, CronTrigger(hour="*"))
    scheduler.start()