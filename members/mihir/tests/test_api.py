"""Mihir: public read-only JSON API."""


def test_list_returns_only_published_newest_first(client, make_announcement):
    make_announcement("Old notice")
    make_announcement("Draft notice", published=False)
    make_announcement("New notice")
    data = client.get("/api/announcements").get_json()
    assert [i["title"] for i in data["items"]] == ["New notice", "Old notice"]
    assert data["total"] == 2


def test_list_filters_by_category_and_keyword(client, make_announcement):
    make_announcement("Exam hall list", category="Examinations")
    make_announcement("Cricket trials", category="Clubs")
    data = client.get("/api/announcements?category=Clubs").get_json()
    assert [i["title"] for i in data["items"]] == ["Cricket trials"]
    assert client.get("/api/announcements?q=exam").get_json()["total"] == 1


def test_invalid_category_is_a_400(client):
    response = client.get("/api/announcements?category=Sports")
    assert response.status_code == 400
    assert "category" in response.get_json()["errors"]


def test_get_one_published(client, make_announcement):
    a_id = make_announcement("Library hours", category="General", venue="Library")
    data = client.get(f"/api/announcements/{a_id}").get_json()
    assert data["title"] == "Library hours" and data["venue"] == "Library"
    assert data["has_poster"] is False


def test_get_one_draft_is_404(client, make_announcement):
    a_id = make_announcement("Secret", published=False)
    assert client.get(f"/api/announcements/{a_id}").status_code == 404
