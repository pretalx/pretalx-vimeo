from django.db import models
from django.utils.html import format_html


class VimeoLink(models.Model):
    submission = models.OneToOneField(
        to="submission.Submission", on_delete=models.CASCADE, related_name="vimeo_link"
    )
    video_id = models.CharField(max_length=20)
    video_hash = models.CharField(max_length=20, blank=True, default="")

    def __str__(self):
        return f"VimeoLink(event={self.submission.event}, submission={self.submission})"

    @property
    def player_link(self):
        if self.video_hash:
            return f"https://player.vimeo.com/video/{self.video_id}?h={self.video_hash}"
        return f"https://player.vimeo.com/video/{self.video_id}"

    @property
    def vimeo_link(self):
        if self.video_hash:
            return f"https://vimeo.com/{self.video_id}/{self.video_hash}"
        return f"https://vimeo.com/video/{self.video_id}"

    @property
    def iframe(self):
        return format_html(
            '<div class="embed-responsive embed-responsive-16by9"><iframe src="{}" frameborder="0" allowfullscreen></iframe></div>',
            self.player_link,
        )

    def serialize(self):
        return {"submission": self.submission.code, "vimeo_link": self.vimeo_link}
