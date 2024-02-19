
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from core.views import error404, error500
from django.contrib.auth.decorators import login_required




urlpatterns = [
    path('developer-admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('booking/', include('booking.urls', namespace='booking')),
]


handler404 = error404
handler500 = error500



urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL,
                      document_root=settings.STATIC_ROOT)