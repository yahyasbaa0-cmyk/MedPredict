import requests
import json

URL = "http://localhost:8000/api/appointments/whatsapp/webhook/"

def send_message(body, phone="whatsapp:+212600000000"):
    data = {
        "Body": body,
        "From": phone
    }
    response = requests.post(URL, data=data)
    print(f"\n--- Sent: {body} ---")
    print(response.text)
    return response

# Test flow
send_message("bonjour")
send_message("oui")
send_message("CD12345") # CIN
send_message("Mohammed") # First name
send_message("Alami") # Last name
send_message("1") # Choix docteur
send_message("25/12/2026") # Date
send_message("10:00") # Heure
