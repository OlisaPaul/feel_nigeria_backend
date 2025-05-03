from django.http import JsonResponse
from .sabre_client import get_sabre_client

def list_supported_countries(request):
    client = get_sabre_client()
    # This matches the example in scabbard docs
    result = client.Air_Utility.V1ListsSupportedCountriesGet(
        pointofsalecountry="US"
    ).result()
    return JsonResponse({
        "PointOfSale": result.PointOfSale,
        "OriginCountries": [
            {"code": c.CountryCode, "name": c.CountryName}
            for c in result.OriginCountries
        ],
        "DestinationCountries": [
            {"code": c.CountryCode, "name": c.CountryName}
            for c in result.DestinationCountries
        ],
    })
