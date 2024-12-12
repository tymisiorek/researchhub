document.addEventListener('DOMContentLoaded', function () {
    /*
*  REFERENCES
*  Title: ChatGPT
*  Author: OpenAI
*  Date: 11/30/2024
*  Used to write the boilerplate for this file and implement the random colors for each user

*  Title: FullCalendar Documentation
*  Date: 12/4/2024
*  Used as the base for the calendar in the app.
* https://fullcalendar.io/docs

*  Title: DateTime Documentation
*  Date: 12/4/2024
*  Used for getting times in adding availability
* https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Date

*  Title: Fetch API
*  Date: 12/4/2024
*  Used for creating error messages/handling
* https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch

*/
    
    var calendarEl = document.getElementById('calendar');
    var availabilityModal = new bootstrap.Modal(document.getElementById('availabilityModal'), {});
    var selectedDate = null;

    var teamId = calendarEl.dataset.teamId;

    //User-to-Color mapping
    const userColorMap = {};
    function getRandomColor() {
        let r, g, b;
        do {
            r = Math.floor(Math.random() * 256);
            g = Math.floor(Math.random() * 256);
            b = Math.floor(Math.random() * 256);
        } while ((r > 200 && g > 200 && b > 200) || (r < 50 && g < 50 && b < 50)); // Avoid too light or dark colors
        return `rgb(${r}, ${g}, ${b})`;
    }

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'timeGridWeek',
        events: function (fetchInfo, successCallback, failureCallback) {
            fetch(`/calendar/${teamId}/data/`)
                .then(response => response.json())
                .then(data => {
                    data.forEach(event => {
                        //Assign a unique color for each user
                        if (!userColorMap[event.owner]) {
                            userColorMap[event.owner] = getRandomColor();
                        }
                        event.color = userColorMap[event.owner];
                    });
                    successCallback(data);
                })
                .catch(error => {
                    console.error("Error fetching events:", error);
                    failureCallback(error);
                });
        },
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'timeGridWeek,dayGridMonth'
        },
        eventClick: function (info) {
            if (confirm(`Do you want to delete this availability for ${info.event.title}?`)) {
                fetch(`/calendar/${teamId}/delete/${info.event.id}/`, {
                    method: 'DELETE',
                    headers: {
                        'X-CSRFToken': getCSRFToken(),
                        'Accept': 'application/json',
                    }
                })
                .then(response => response.json().then(data => ({ status: response.status, body: data })))
                .then(({ status, body }) => {
                    if (status === 200 && body.success) {
                        calendar.refetchEvents();
                        alert("Availability deleted successfully.");
                    } else {
                        alert(`Error: ${body.error}`);
                    }
                })
                .catch(error => {
                    console.error("Error deleting availability:", error);
                    alert("An error occurred while deleting the availability.");
                });
            }
        },
        dateClick: function (info) {
            selectedDate = info.dateStr.split('T')[0];
            document.getElementById('availability-date').value = selectedDate;
            document.getElementById('start-time').value = '';
            document.getElementById('end-time').value = '';
            document.getElementById('form-errors').innerHTML = '';
            availabilityModal.show();
        },
        slotMinTime: "08:00:00",
        slotMaxTime: "23:59:59"
    });
    calendar.render();

    document.getElementById('availabilityForm').addEventListener('submit', function (event) {
        event.preventDefault();
        var date = document.getElementById('availability-date').value;
        var startTime = document.getElementById('start-time').value;
        var endTime = document.getElementById('end-time').value;
        var csrfToken = getCSRFToken();
        var now = new Date();
        var startDateTime = new Date(`${date}T${startTime}`);
        var endDateTime = new Date(`${date}T${endTime}`);

        if (startTime >= endTime) {
            document.getElementById('form-errors').innerHTML = 'End time must be after start time.';
            return;
        }

        if (startDateTime < now) {
            document.getElementById('form-errors').innerHTML = 'You cannot create an availability in the past.';
            return;
        }

        fetch(`/calendar/${teamId}/add/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
                'Accept': 'application/json',
            },
            body: JSON.stringify({
                date: date,
                start_time: startTime,
                end_time: endTime
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                availabilityModal.hide();
                calendar.refetchEvents();
            } else if (data.error === 'Error: You are not authorized to add availability for this team.') {
                alert('Error: You are not authorized to add availability for this team.');
            } else if (data.error === 'End time must be after start time.') {
                document.getElementById('form-errors').innerHTML = data.error;
            } else {
                document.getElementById('form-errors').innerHTML = data.error;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('form-errors').innerHTML = 'Error: You are not authorized to add availability for this team.';
        });
    });

    function getCSRFToken() {
        var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }
});
