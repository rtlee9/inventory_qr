from django.urls import path

from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    path("", views.list_view, name="list"),
    path("detail/<int:pk>/", views.detail_view, name="detail"),
    path("create", views.Create.as_view(), name="create"),
]
