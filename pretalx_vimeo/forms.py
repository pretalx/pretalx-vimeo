from django import forms
from django.utils.translation import gettext_lazy as _


class VimeoUrlForm(forms.Form):

    vimeo_url = forms.URLField(required=False)

    def __init__(self, *args, **kwargs):
        self.submission = kwargs.pop("submission")
        initial = kwargs.get("initial", dict())
        initial["vimeo_url"] = self.submission.event.settings.get(
            f"vimeo_url_{self.submission.code}"
        )
        kwargs["initial"] = initial
        super().__init__(*args, **kwargs)
        self.fields["vimeo_url"].label = self.submission.title

    def clean_vimeo_url(self):
        from .recording import is_vimeo_url

        data = self.cleaned_data["vimeo_url"]
        if not is_vimeo_url(data):
            raise forms.ValidationError(_("Please provide a vimeo.com URL!"))
        return data
