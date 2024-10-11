from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from event.views import all_events
from core.views import index, terms, privacy

urlpatterns = [
    path("", index, name="index"),
    path("list/", all_events, name="all_events"),
    path('admin/', admin.site.urls),
    path("detect/", include("detect.urls")),
    path("event/", include("event.urls")),
    path("accounts/", include("account.urls")),
    path("terms/", terms, name="terms"),
    path("privacy/", privacy, name="privacy"),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

