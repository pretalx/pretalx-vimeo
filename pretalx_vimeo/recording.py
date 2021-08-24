from pretalx.agenda.recording import BaseRecordingProvider


def is_vimeo_url(url):
    return "vimeo.com/" in url  # TODO better validation


def get_embed_url(url):
    if "player.vimeo.com" in url:
        return url
    if not is_vimeo_url(url):
        return

    url = url[url.find("vimeo.com/") + len("vimeo.com/") :]
    video_id = url.split("/")[0]
    return f"https://player.vimeo.com/video/{video_id}"


class VimeoProvider(BaseRecordingProvider):
    def get_recording(self, submission):
        path = self.event.settings.get(f"vimeo_url_{submission.code}")
        if not path:
            return
        url = get_embed_url(path)
        if not url:
            return
        iframe = f'<div class="embed-responsive embed-responsive-16by9"><iframe src="{url}" frameborder="0" allowfullscreen></iframe></div>'
        csp_header = "https://player.vimeo.com"
        return {"iframe": iframe, "csp_header": csp_header}
