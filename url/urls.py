from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    # path("", views.index, name="index"),
    path("", login_required(views.list_view), name="list"),
    path("detail/<int:pk>/", login_required(views.detail_view), name="detail"),
    path("create", login_required(views.Create.as_view()), name="create"),
]
