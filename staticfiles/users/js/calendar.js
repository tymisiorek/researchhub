document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');
    var availabilityModal = new bootstrap.Modal(document.getElementById('availabilityModal'), {});
    var selectedDate = null;

    var calendar = new FullCalendar.Calendar(calendarEl, {
        initialView: 'dayGridMonth',
        events: '/calendar/data/',  // URL for fetching events data
        eventColor: '#378006',
        eventClick: function(info) {
            console.log("Event Clicked:", info.event);  // Debugging
            console.log("Event ID:", info.event.id);    // Debugging

            if (info.event.id) {  // Proceed only if ID exists
                if (confirm(`Do you want to delete the availability for ${info.event.title}?`)) {
                    fetch(`/calendar/delete/${info.event.id}/`, {
                        method: 'DELETE',
                        headers: {
                            'X-CSRFToken': getCSRFToken()
                        }
                    })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.json();
                    })
                    .then(data => {
                        if (data.success) {
                            calendar.refetchEvents();  // Refresh calendar events
                            alert("Availability deleted successfully.");
                        } else {
                            alert("Error: Could not delete availability.");
                        }
                    })
                    .catch(error => {
                        console.error("Error deleting availability:", error);
                        alert("An error occurred while deleting the availability.");
                    });
                }
            }
        },
        dateClick: function(info) {
            selectedDate = info.dateStr;
            document.getElementById('availability-date').value = selectedDate;
            document.getElementById('start-time').value = '';
            document.getElementById('end-time').value = '';
            document.getElementById('form-errors').innerHTML = '';
            availabilityModal.show();
        }
    });
    calendar.render();

    document.getElementById('availabilityForm').addEventListener('submit', function(event) {
        event.preventDefault();
        var date = document.getElementById('availability-date').value;
        var startTime = document.getElementById('start-time').value;
        var endTime = document.getElementById('end-time').value;
        var csrfToken = getCSRFToken();

        if (startTime >= endTime) {
            document.getElementById('form-errors').innerHTML = 'End time must be after start time.';
            return;
        }

        fetch('/calendar/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
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
            } else {
                document.getElementById('form-errors').innerHTML = data.error;
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('form-errors').innerHTML = 'An error occurred. Please try again.';
        });
    });

    // Helper function to get CSRF token from the form
    function getCSRFToken() {
        var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        return csrfToken ? csrfToken.value : '';
    }
});
