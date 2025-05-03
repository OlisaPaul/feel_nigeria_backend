import json
import os
import scabbard
from django.conf import settings

def get_sabre_client():
    # 1. Ensure the API config file exists
    config = {
        "clientId": os.getenv('SABRE_CLIENT_ID'),
        "clientSecret": os.getenv('SABRE_CLIENT_SECRET'),
        "environment": os.getenv('SABRE_ENVIRONMENT'),
        "group":   os.getenv('SABRE_GROUP'),
        "domain":  os.getenv('SABRE_DOMAIN'),
        "formatVersion": os.getenv('SABRE_FORMAT_VERSION'),
    }
    config_path = os.path.join(settings.BASE_DIR, "api_connect_parameters.json")
    with open(config_path, "w") as f:
        json.dump(config, f)

    # 2. Instantiate and return the client
    return scabbard.get_client()
