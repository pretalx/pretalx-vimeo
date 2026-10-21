import copy
import re
from urllib.parse import parse_qs, urlsplit

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import VimeoLink

VIMEO_HASH = re.compile(r"^[0-9a-f]{1,20}$")


def parse_vimeo_url(value):
    url = urlsplit(value)
    hostname = url.hostname or ""
    if hostname != "vimeo.com" and not hostname.endswith(".vimeo.com"):
        return None
    parts = [part for part in url.path.split("/") if part]
    # Showcase URLs contain the showcase ID before /video/<id>.
    if "video" in parts:
        parts = parts[parts.index("video") + 1 :]
    for index, part in enumerate(parts):
        if part.isdigit() and len(part) <= 20:
            following = parts[index + 1] if index + 1 < len(parts) else ""
            video_hash = parse_qs(url.query).get("h", [following])[0]
            if not VIMEO_HASH.match(video_hash):
                video_hash = ""
            return part, video_hash
    return None


class VimeoUrlForm(forms.Form):
    def __init__(self, *args, event, **kwargs):
        super().__init__(*args, **kwargs)

        if not event or not event.current_schedule:
            return

        self.talks = (
            event.current_schedule.talks.all()
            .filter(is_visible=True, submission__isnull=False)
            .select_related("submission", "submission__event")
            .order_by("start")
        )
        vimeo_data = {
            v.submission.code: v.vimeo_link
            for v in VimeoLink.objects.filter(submission__event=event).select_related(
                "submission"
            )
        }
        s = _("Go to video")
        p = _("Go to talk page.")
        for talk in self.talks:
            link = vimeo_data.get(talk.submission.code)
            help_text = f'<a href="{talk.submission.urls.public.full()}" target="_blank">{p}</a>'
            if link:
                help_text += f' | <a href="{link}" target="_blank">{s}</a>'
            self.fields[f"video_id_{talk.submission.code}"] = forms.URLField(
                required=False,
                label=talk.submission.title,
                widget=forms.TextInput(attrs={"placeholder": ""}),
                initial=link,
                help_text=help_text,
            )

    def clean(self):
        result = {}
        for key, value in copy.copy(self.cleaned_data).items():
            if not value:
                result[key] = None
            elif not (parsed := parse_vimeo_url(value)):
                self.add_error(key, _("Please provide a Vimeo URL!"))
            else:
                result[key] = parsed
        return result

    def save(self):
        for talk in self.talks:
            parsed = self.cleaned_data.get(f"video_id_{talk.submission.code}")
            if parsed:
                video_id, video_hash = parsed
                VimeoLink.objects.update_or_create(
                    submission=talk.submission,
                    defaults={"video_id": video_id, "video_hash": video_hash},
                )
            else:
                VimeoLink.objects.filter(submission=talk.submission).delete()
