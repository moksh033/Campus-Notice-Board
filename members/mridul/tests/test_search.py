"""Mridul: keyword search and category filtering."""
from app.services import search_service


def titles(app, **kw):
    with app.app_context():
        return [a.title for a in search_service.search_announcements(**kw).items]


def test_search_matches_title_description_and_venue_case_insensitively(app, make_announcement):
    make_announcement("Robotics workshop", category="Clubs")
    make_announcement("Fee deadline", category="General", description="Pay at the ACCOUNTS office")
    make_announcement("Annual day", category="Events", venue="Open Air Theatre")
    assert titles(app, q="ROBOTICS") == ["Robotics workshop"]
    assert titles(app, q="accounts") == ["Fee deadline"]
    assert titles(app, q="theatre") == ["Annual day"]


def test_category_filter(app, make_announcement):
    make_announcement("A", category="Events")
    make_announcement("B", category="Clubs")
    assert titles(app, category="Events") == ["A"]


def test_search_and_category_combine(app, make_announcement):
    make_announcement("Coding contest", category="Events")
    make_announcement("Coding club meet", category="Clubs")
    assert titles(app, q="coding", category="Clubs") == ["Coding club meet"]


def test_results_are_newest_first(app, make_announcement):
    for name in ("First", "Second", "Third"):
        make_announcement(name)
    assert titles(app) == ["Third", "Second", "First"]


def test_unpublished_never_appear_in_results(app, make_announcement):
    make_announcement("Secret exam draft", published=False)
    assert titles(app, q="secret") == []


def test_percent_and_underscore_are_matched_literally(app, make_announcement):
    make_announcement("Plain title")
    make_announcement("100% attendance rule")
    assert titles(app, q="%") == ["100% attendance rule"]
    assert titles(app, q="_") == []


def test_invalid_category_is_ignored(app, make_announcement):
    make_announcement("Only one")
    assert titles(app, category="Sports") == ["Only one"]


def test_dashboard_search_and_empty_results(client, make_announcement):
    make_announcement("Placement talk", category="General")
    assert b"Placement talk" in client.get("/?q=placement").data
    empty = client.get("/?q=zzzz&category=Events")
    assert b"No announcements found" in empty.data and b"Clear filters" in empty.data


def test_search_text_is_escaped_in_the_page(client):
    assert b"<script>" not in client.get("/?q=<script>alert(1)</script>").data
