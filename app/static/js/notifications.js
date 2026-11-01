// Notification bell. Owner: Mridul.
(function () {
  "use strict";

  var bell = document.querySelector("[data-bell]");
  if (!bell) { return; }

  var toggle = bell.querySelector("[data-bell-toggle]");
  var panel = bell.querySelector("[data-bell-panel]");
  var countBadge = bell.querySelector("[data-bell-count]");
  var markAll = bell.querySelector("[data-mark-all]");
  var tokenTag = document.querySelector('meta[name="csrf-token"]');
  var csrfToken = tokenTag ? tokenTag.getAttribute("content") : "";

  function setOpen(open) {
    panel.hidden = !open;
    toggle.setAttribute("aria-expanded", String(open));
  }

  function setUnread(count) {
    countBadge.textContent = String(count);
    countBadge.hidden = count === 0;
    if (markAll) { markAll.hidden = count === 0; }
    toggle.setAttribute("aria-label", "Notifications, " + count + " unread");
  }

  function post(url) {
    return fetch(url, {
      method: "POST",
      headers: { "X-CSRFToken": csrfToken },
      credentials: "same-origin",
      keepalive: true
    }).then(function (response) { return response.json(); });
  }

  toggle.addEventListener("click", function () { setOpen(panel.hidden); });

  document.addEventListener("click", function (event) {
    if (!bell.contains(event.target)) { setOpen(false); }
  });
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && !panel.hidden) { setOpen(false); toggle.focus(); }
  });

  // Opening a notification marks it read, then the browser follows the link as normal.
  panel.querySelectorAll("[data-notification-id]").forEach(function (link) {
    link.addEventListener("click", function () {
      post("/api/notifications/" + link.getAttribute("data-notification-id") + "/read");
    });
  });

  if (markAll) {
    markAll.addEventListener("click", function () {
      post("/api/notifications/read-all").then(function () {
        panel.querySelectorAll("li.unread").forEach(function (item) { item.classList.remove("unread"); });
        setUnread(0);
      });
    });
  }
})();
