# -*- coding: UTF-8 -*-
from django.urls import path,include
from django.contrib import admin

admin.autodiscover()

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler500
from recomendacion import login
urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'', include('recomendacion.urls')),

]
# ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# handler404 = login.Error404View.as_view()
# handler500 = login.Error500View.as_error_view()
