import pytest
from django.urls import reverse
from django_scopes import scopes_disabled

from pretalx_vimeo.models import VimeoLink
from pretalx_vimeo.recording import VimeoProvider

SETTINGS_URL_NAME = "plugins:pretalx_vimeo:settings"
API_LIST_URL_NAME = "plugins:pretalx_vimeo:api_list"
API_SINGLE_URL_NAME = "plugins:pretalx_vimeo:api_single"


@pytest.mark.django_db
def test_orga_can_access_settings(orga_client, event):
    response = orga_client.get(
        reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug}),
        follow=True,
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_reviewer_cannot_access_settings(review_client, event):
    response = review_client.get(
        reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug}),
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_settings_without_schedule_shows_info(orga_client, event):
    response = orga_client.get(
        reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug}),
        follow=True,
    )
    assert response.status_code == 200
    assert b"schedule" in response.content.lower()


@pytest.mark.django_db
def test_post_without_schedule_shows_error(orga_client, event):
    response = orga_client.post(
        reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug}),
        data={},
        follow=True,
    )
    assert response.status_code == 200


@pytest.mark.django_db
def test_orga_can_save_vimeo_url(orga_client, event, submission, schedule):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.post(
        url,
        {f"video_id_{submission.code}": "https://vimeo.com/123456789"},
        follow=True,
    )
    assert response.status_code == 200
    with scopes_disabled():
        link = VimeoLink.objects.get(submission=submission)
        assert link.video_id == "123456789"


@pytest.mark.django_db
def test_orga_invalid_url_rejected(orga_client, event, submission, schedule):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.post(
        url,
        {f"video_id_{submission.code}": "https://youtube.com/watch?v=abc"},
        follow=True,
    )
    assert response.status_code == 200
    with scopes_disabled():
        assert not VimeoLink.objects.filter(submission=submission).exists()


@pytest.mark.django_db
def test_orga_can_clear_vimeo_url(orga_client, event, submission, schedule, vimeo_link):
    url = reverse(SETTINGS_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.post(
        url,
        {f"video_id_{submission.code}": ""},
        follow=True,
    )
    assert response.status_code == 200
    with scopes_disabled():
        assert not VimeoLink.objects.filter(submission=submission).exists()


@pytest.mark.django_db
def test_api_list(orga_client, event, vimeo_link):
    url = reverse(API_LIST_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 1
    assert data["results"][0]["submission"] == vimeo_link.submission.code


@pytest.mark.django_db
def test_api_list_empty(orga_client, event):
    url = reverse(API_LIST_URL_NAME, kwargs={"event": event.slug})
    response = orga_client.get(url)
    assert response.status_code == 200
    assert response.json()["results"] == []


@pytest.mark.django_db
def test_api_single(orga_client, event, submission, vimeo_link):
    url = reverse(
        API_SINGLE_URL_NAME,
        kwargs={"event": event.slug, "code": submission.code},
    )
    response = orga_client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["submission"] == submission.code
    assert "vimeo.com" in data["vimeo_link"]


@pytest.mark.django_db
def test_api_single_no_link(orga_client, event, submission):
    url = reverse(
        API_SINGLE_URL_NAME,
        kwargs={"event": event.slug, "code": submission.code},
    )
    response = orga_client.get(url)
    assert response.status_code == 200
    assert response.json() == {}


@pytest.mark.django_db
def test_api_single_not_found(orga_client, event):
    url = reverse(
        API_SINGLE_URL_NAME,
        kwargs={"event": event.slug, "code": "ZZZZZZ"},
    )
    response = orga_client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_api_anonymous_returns_404(client, event):
    url = reverse(API_LIST_URL_NAME, kwargs={"event": event.slug})
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_vimeo_link_properties(vimeo_link):
    assert vimeo_link.player_link == "https://player.vimeo.com/video/123456789"
    assert vimeo_link.vimeo_link == "https://vimeo.com/video/123456789"
    assert "iframe" in vimeo_link.iframe
    assert "player.vimeo.com" in vimeo_link.iframe
    serialized = vimeo_link.serialize()
    assert serialized["submission"] == vimeo_link.submission.code
    assert serialized["vimeo_link"] == vimeo_link.vimeo_link


@pytest.mark.django_db
def test_recording_provider_with_link(event, submission, vimeo_link):
    provider = VimeoProvider(event)
    recording = provider.get_recording(submission)
    assert recording is not None
    assert "iframe" in recording
    assert recording["csp_header"] == "https://player.vimeo.com"


@pytest.mark.django_db
def test_recording_provider_without_link(event, submission):
    provider = VimeoProvider(event)
    recording = provider.get_recording(submission)
    assert recording is None
