import os
import requests
import sendgrid
import json
from sendgrid.helpers.mail import Mail, Email, To


def fetch_subscribers_per_page(list_id=None, page_size=1000, page_token=None):
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
    query_params = {}
    
    if list_id:
        query_params["list_ids"] = list_id  
    if page_size:
        query_params["page_size"] = page_size
    if page_token:
        query_params["page_token"] = page_token
    
    response = sg.client.marketing.contacts.get(query_params=query_params)
    
    # The SDK returns a Response object containing .status_code, .body, etc.
    if response.status_code == 200:
        data = json.loads(response.body)
        # 'data' is a dictionary; contacts live under "result" (if present)
        contacts = data.get("result", [])
        return data, contacts
    else:
        print(f"Failed to fetch contacts. Status: {response.status_code}, Body: {response.body}")
        return None, []

def fetch_all_subscribers(list_id=None):
    all_contacts = []
    page_token = None
    
    while True:
        data, contacts = fetch_subscribers_per_page(list_id=list_id, page_token=page_token)
        if not data or not contacts:
            break  # No more contacts or error occurred
        
        all_contacts.extend(contacts)
        
        # Check for next page
        next_page_token = data.get("next_page_token")
        if next_page_token:
            page_token = next_page_token
        else:
            break  # No more pages
    
    return all_contacts

def send_daily_newsletter(content):
    sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))

    list_id = os.getenv("MAILER_LIST_ID")
    from_email = Email(os.getenv("MAILER_FROM_EMAIL"))
    
    subscribers = fetch_all_subscribers(list_id)

    for contact in subscribers:
        email = contact["email"]
        message = Mail(
            from_email=from_email,
            to_emails=To(email),
            subject=content["subject"],
            html_content=content["body"],
        )
        response = sg.send(message)
        print(f"Sent to {email}, status code: {response.status_code}")
