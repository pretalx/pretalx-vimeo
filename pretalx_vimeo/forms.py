import copy

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import VimeoLink


class VimeoUrlForm(forms.Form):
    def __init__(self, *args, event, **kwargs):
        if not event.current_schedule:
            return super().__init__(*args, **kwargs)

        super().__init__(*args, **kwargs)

        self.talks = (
            event.current_schedule.talks.all()
            .filter(is_visible=True, submission__isnull=False)
            .order_by("start")
        )
        vimeo_data = {
            v.submission.code: v.vimeo_link
            for v in VimeoLink.objects.filter(submission__event=event)
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
            elif "vimeo.com" not in value:
                self.add_error(key, _("Please provide a Vimeo URL!"))
            else:
                parts = [v for v in value.split("/") if v]
                result[key] = parts[-1]
        return result

    def save(self):
        for talk in self.talks:
            video_id = self.cleaned_data.get(f"video_id_{talk.submission.code}")
            if video_id:
                VimeoLink.objects.update_or_create(
                    submission=talk.submission, defaults={"video_id": video_id}
                )
            else:
                VimeoLink.objects.filter(submission=talk.submission).delete()
