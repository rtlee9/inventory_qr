from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    path("", login_required(views.MostRecentView.as_view()), name="most_recent"),
    path("history/", login_required(views.AllView.as_view()), name="history"),
    path("detail/<int:pk>/", login_required(views.DetailView.as_view()), name="detail"),
    path("create", login_required(views.Create.as_view()), name="create"),
]
