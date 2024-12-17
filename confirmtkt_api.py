import requests
import json

# """ Format of arguments"""
# from_station = "NDLS"
# to_station = "MMCT"
# date_of_journey = "18-12-2024"


def get_train_booking_data(fromStnCode, toStnCode, doj):
   
    url = "https://securedapi.confirmtkt.com/api/platform/trainbooking/tatwnstns"
    params = {
        "fromStnCode": fromStnCode,
        "destStnCode": toStnCode,
        "doj": doj,
        "token": "368223F820EBEB8BFA467209CD49702C69606FF2E32B502EA377C65EA9A2031E",  # Your token
        "quota": "GN",
        "appVersion": "290"
    }

    # Send the GET request
    response = requests.get(url, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Return the JSON response
        
        return response.json()
    else:
        # Return an error message if the request failed
        return {"error": f"Error: {response.status_code}"}


