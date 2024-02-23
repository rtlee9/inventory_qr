from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("", include("url.urls")),
    path("admin/", admin.site.urls),
    path(
        "accounts/login/", auth_views.LoginView.as_view(next_page="most_recent"), name="login"
    ),
    path(
        "accounts/logout/",
        auth_views.LogoutView.as_view(next_page="login"),
        name="logout",
    ),
    path("accounts/", include("django_registration.backends.one_step.urls")),
    # path("accounts/", include("django.contrib.auth.urls")),
]

if settings.DEBUG:
    import debug_toolbar

    # Server statics and uploaded media
    # Allow error pages to be tested
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
