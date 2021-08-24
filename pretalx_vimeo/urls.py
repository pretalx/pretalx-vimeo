from django.urls import re_path
from pretalx.event.models.event import SLUG_CHARS

from .views import VimeoSettings

urlpatterns = [
    re_path(
        fr"^orga/event/(?P<event>[{SLUG_CHARS}]+)/settings/p/vimeo/$",
        VimeoSettings.as_view(),
        name="settings",
    )
]
