"""Shared constants. Owner: Mihir. Everyone imports from here instead of repeating values."""

CATEGORIES = ("Examinations", "Events", "Clubs", "General")

TITLE_MAX = 150
VENUE_MAX = 150
LINK_MAX = 500

POSTER_EXTENSIONS = ("png", "jpg", "jpeg", "webp")
PDF_EXTENSIONS = ("pdf",)
POSTER_MAX_BYTES = 3 * 1024 * 1024
PDF_MAX_BYTES = 5 * 1024 * 1024

NOTIFICATION_LIMIT = 10  # how many recent notifications the bell shows
