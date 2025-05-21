document.addEventListener('DOMContentLoaded', function () {
  const calendarBtn = document.getElementById('calendarBtn');
  if (!calendarBtn) return;

  calendarBtn.addEventListener('click', () => {
    const main = document.querySelector("main");
    main.innerHTML = `<div id="calendar-container" style="margin-top: 2rem;"></div>`;
    const calendarEl = document.getElementById('calendar-container');

    fetch("/api/events")
      .then(res => res.json())
      .then(events => {
        const calendar = new FullCalendar.Calendar(calendarEl, {
          initialView: "dayGridMonth",
          locale: "ja",
          selectable: true,
          headerToolbar: {
            left: "prev,next",
            center: "title",
            right: "today,dayGridMonth,timeGridWeek"
          },
          events: events,
          dateClick: function (info) {
            const title = prompt(`${info.dateStr} に追加する予定:`);
            if (title) {
              const eventData = {
                title: title,
                start: info.dateStr
              };

              fetch("/api/events", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(eventData)
              })
              .then(res => res.json())
              .then(newEvent => {
                calendar.addEvent({
                  ...eventData,
                  id: newEvent.id,
                  allDay: true
                });
              });
            }
          },
          eventClick: function (info) {
            const confirmDelete = confirm(`「${info.event.title}」を削除しますか？`);
            if (confirmDelete) {
              fetch("/api/events", {
                method: "DELETE",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ id: info.event.id })
              })
              .then(() => {
                info.event.remove();
              });
            }
          }
        });

        calendar.render();
      });
  });
});