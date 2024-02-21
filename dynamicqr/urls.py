from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path

urlpatterns = [
    path("", include("url.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    import debug_toolbar

    # Server statics and uploaded media
    # urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Allow error pages to be tested
    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
