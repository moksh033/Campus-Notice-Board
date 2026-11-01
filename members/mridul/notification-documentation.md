# Notification System Documentation – Mridul

## 1. Overview
The CampusConnect notification system informs students when new announcements are published. Students can view notifications through the notification bell on the homepage.

## 2. Notification Features

| Action | Expected Result |
|---|---|
| Publish an announcement | Creates one notification record. |
| Open a notification | Marks that notification as read in the current browser session. |
| Mark all as read | Marks all recent notifications as read in the current browser session. |
| Unpublish or delete | Removes the associated notification. |
| Open a new browser or clear cookies | Notifications appear unread again. |

## 3. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/notifications` | Retrieves recent notifications and unread count. |
| POST | `/api/notifications/<id>/read` | Marks an individual notification as read. |
| POST | `/api/notifications/read-all` | Marks all recent notifications as read. |

## 4. Notification Display
- The notification bell displays the unread count.
- The dropdown displays the 10 most recent notifications.
- Each notification links to its corresponding announcement.
- Read and unread notifications have different visual styles.

## 5. Read Status Management
Read status is stored in the browser session using `session["read_notification_ids"]`.

Since students do not have individual accounts, this approach ensures that one browser's read actions do not affect other browsers.

## 6. Current Limitation
The notification count updates when the page is loaded. Real-time push notifications are not currently implemented.

## 7. Testing
The notification functionality was tested locally, including:
- Notification creation after publishing.
- Notification bell display.
- Unread count.
- Individual mark-as-read.
- Mark-all-as-read.
