from django.dispatch import receiver
from django.urls import reverse

from pretalx.agenda.signals import register_recording_provider
from pretalx.orga.signals import nav_event_settings


@receiver(register_recording_provider)
def vimeo_provider(sender, **kwargs):
    from .recording import VimeoProvider  # noqa: PLC0415

    return VimeoProvider(sender)


@receiver(nav_event_settings)
def vimeo_settings(sender, request, **kwargs):
    if not request.user.has_perm("event.update_event", request.event):
        return []
    return [
        {
            "label": "Vimeo",
            "url": reverse(
                "plugins:pretalx_vimeo:settings", kwargs={"event": request.event.slug}
            ),
            "active": request.resolver_match.url_name
            == "plugins:pretalx_vimeo:settings",
        }
    ]
