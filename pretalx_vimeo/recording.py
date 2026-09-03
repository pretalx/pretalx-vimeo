from pretalx.agenda.recording import BaseRecordingProvider

from .models import VimeoLink


class VimeoProvider(BaseRecordingProvider):
    def get_recording(self, submission):
        vimeo = VimeoLink.objects.filter(submission=submission).first()
        if vimeo:
            return {"iframe": vimeo.iframe, "csp_header": "https://player.vimeo.com"}
