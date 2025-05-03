# sabre_integration/urls.py
from django.urls import path
from . import views

app_name = 'sabre'  # namespacing your URLs

urlpatterns = [
    # GET /sabre/countries/ → list_supported_countries view
    path(
        'countries/',
        views.list_supported_countries,
        name='list_countries'
    ),
    # you can add more endpoints here, e.g. path('flights/', views.search_flights, name='search_flights')
]