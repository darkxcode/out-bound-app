from django.conf.urls import url, include
from django.contrib import admin

from apps.campaigns.views import open_message_tracker

urlpatterns = [
    url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url(r'^', admin.site.urls),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^contact/(?P<contact_email>\w+|[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/open_message/$',
        open_message_tracker, name="open_message_tracker"),
]
