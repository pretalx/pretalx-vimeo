import copy

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import VimeoLink


class VimeoUrlForm(forms.Form):
    def __init__(self, *args, event, **kwargs):
        if not event.current_schedule:
            return super().__init__(*args, **kwargs)

        self.talks = (
            event.current_schedule.talks.all()
            .filter(is_visible=True, submission__isnull=False)
            .order_by("start")
        )
        initial = kwargs.get("initial", dict())
        vimeo_data = {
            v.submission.code: v.video_id
            for v in VimeoLink.objects.filter(submission__event=event)
        }
        for code, video_id in vimeo_data.items():
            initial[f"video_id_{code}"] = f"https://vimeo.com/{video_id}"

        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)

        for talk in self.talks:
            self.fields[f"video_id_{talk.submission.code}"] = forms.URLField(
                required=False,
                label=talk.submission.title,
                widget=forms.TextInput(attrs={"placeholder": ""}),
            )

    def clean(self):
        result = {}
        for key, value in copy.copy(self.cleaned_data).items():
            if not value:
                result[key] = None
            elif "vimeo.com" not in value:
                self.add_error(key, _("Please provide a Vimeo URL!"))
            else:
                parts = [v for v in value.split("/") if v]
                result[key] = parts[-1]
        return result

    def save(self):
        for talk in self.talks:
            video_id = self.cleaned_data.get("video_id_{talk.submission.code}")
            if video_id:
                VimeoLink.objects.update_or_create(
                    submission=talk.submission, defaults={"video_id": video_id}
                )
            else:
                VimeoLink.objects.filter(submission=talk.submission).delete()
