from django.conf.urls import url, include
from django.contrib import admin

from rest_framework_swagger.views import get_swagger_view

schema_view = get_swagger_view(title='swagger')

prefix = r'^api/v1/'

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^docs/', schema_view, name='swagger'),

    url(prefix, include([
        url(r'^accounts/', include("accounts.urls", namespace="accounts")),
    ])),
]
