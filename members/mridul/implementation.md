# Implementation Notes – Mridul

## 1. Keyword Search
- Supports case-insensitive searches across announcement titles, descriptions and venues.
- Special characters such as `%`, `_` and `\` are escaped so they are treated as literal characters.
- Only published announcements are displayed.

## 2. Category Filtering
- Supports four categories: Examinations, Events, Clubs and General.
- Invalid category values are ignored on the student dashboard.
- Keyword search and category filtering can be applied together.

## 3. Sorting and Pagination
- Announcements are displayed in newest-first order using `published_at`.
- Announcement ID is used as a secondary sorting condition when publication dates are equal.
- Displays 9 announcements per page.

## 4. Empty Search Results
- Displays an appropriate message when no announcements match the search.
- Provides an option to clear filters and view announcements again.

## 5. Notification System
- Creates a notification when an announcement is published.
- Prevents duplicate notifications for the same announcement.
- Removes notifications when an announcement is unpublished or deleted.
- Displays the 10 most recent notifications.

## 6. Notification Bell
- Displays notifications in a dropdown panel.
- Shows the unread notification count.
- Provides individual and mark-all-as-read functionality.
- Links each notification to its corresponding announcement.

## 7. Read Status Management
- Clicking a notification marks it as read.
- Read notification IDs are stored in the browser session.
- Students do not need accounts to receive notifications.

## 8. Design Decision
The project does not have student accounts. Therefore, notification read status is stored separately in each browser session instead of using a shared database `is_read` column. This prevents one browser's read actions from marking notifications as read for everyone.

## 9. Current Limitation
The notification count updates when the page is loaded. Real-time push notifications are not currently implemented.