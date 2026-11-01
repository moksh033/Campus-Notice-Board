# Mridul: Search, Filtering and Notification System

**Branch:** `feature/search-notifications`

## What I own
| File | Purpose |
|---|---|
| `app/services/search_service.py` | Keyword search, category filter, newest-first, pagination |
| `app/models/notification.py`, `app/services/notification_service.py` | Notification table and logic |
| `app/routes/notifications.py` | Bell data (JSON), mark read, mark all read, template context |
| `app/templates/partials/_notification_bell.html`, `app/static/css/notifications.css`, `app/static/js/notifications.js` | Bell interface |

## Tests
`members/mridul/tests/test_search.py`, `test_notifications.py`. Run: `python -m pytest members/mridul`.

## How it connects to the others
Mihir's publish/unpublish/delete calls my `notify_published` and `remove_for`. Moksh's dashboard calls `search_announcements`, and his `base.html` includes my bell partial.
See [implementation.md](implementation.md) and [notification-documentation.md](notification-documentation.md).


## Verification and Testing

### Automated Testing
- Member 5 tests: 21 passed.
- Complete project test suite: 111 passed.

### Manual Testing
The following features were tested locally:
- Keyword search using announcement titles.
- Category-based filtering.
- Newest-first announcement sorting.
- Empty search results.
- Notification bell and unread count.
- Individual notification mark-as-read.
- Mark all notifications as read.

All tested features worked as expected.