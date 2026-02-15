from django.urls import path

from . import api

urlpatterns = [
    path("urls/", api.url_list, name="api_url_list"),
    path("urls/<str:key>/", api.url_detail, name="api_url_detail"),
    path("urls/<str:key>/track/", api.url_track, name="api_url_track"),
    path("urls/<str:key>/qr/", api.url_qr, name="api_url_qr"),
]
