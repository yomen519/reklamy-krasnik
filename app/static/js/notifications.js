// Obsługa systemu powiadomień
document.addEventListener('DOMContentLoaded', function() {
    // Elementy DOM
    const notificationBadge = document.getElementById('notification-badge');
    const notificationsContainer = document.getElementById('notifications-container');
    
    // Funkcja pobierająca liczbę nieprzeczytanych powiadomień
    function fetchUnreadCount() {
        fetch('/notifications/api/unread-count')
            .then(response => response.json())
            .then(data => {
                if (data.count > 0) {
                    notificationBadge.textContent = data.count;
                    notificationBadge.style.display = 'inline';
                } else {
                    notificationBadge.style.display = 'none';
                }
            })
            .catch(error => console.error('Błąd pobierania liczby powiadomień:', error));
    }
    
    // Funkcja pobierająca najnowsze powiadomienia
    function fetchRecentNotifications() {
        fetch('/notifications/api/recent')
            .then(response => response.json())
            .then(data => {
                // Czyścimy kontener
                notificationsContainer.innerHTML = '';
                
                if (data.notifications && data.notifications.length > 0) {
                    // Dodajemy każde powiadomienie
                    data.notifications.forEach(notification => {
                        const notificationHtml = `
                            <a class="dropdown-item ${!notification.is_read ? 'bg-light' : ''}" href="${notification.target_url || '#'}">
                                <div class="d-flex w-100 justify-content-between">
                                    <h6 class="mb-1">${notification.title}</h6>
                                    <small class="text-muted">${new Date(notification.created_at).toLocaleDateString()}</small>
                                </div>
                                <small class="text-muted">${notification.message}</small>
                            </a>
                        `;
                        
                        notificationsContainer.innerHTML += notificationHtml;
                    });
                } else {
                    // Brak powiadomień
                    notificationsContainer.innerHTML = `
                        <div class="dropdown-item text-center text-muted">
                            Brak nowych powiadomień
                        </div>
                    `;
                }
            })
            .catch(error => {
                console.error('Błąd pobierania powiadomień:', error);
                notificationsContainer.innerHTML = `
                    <div class="dropdown-item text-center text-danger">
                        Błąd ładowania powiadomień
                    </div>
                `;
            });
    }
    
    // Inicjalne pobranie danych
    if (notificationBadge && notificationsContainer) {
        fetchUnreadCount();
        
        // Pobierz najnowsze powiadomienia przy kliknięciu w dzwonek
        const notificationsDropdown = document.getElementById('notificationsDropdown');
        if (notificationsDropdown) {
            notificationsDropdown.addEventListener('show.bs.dropdown', fetchRecentNotifications);
        }
        
        // Odświeżaj liczbę powiadomień co 60 sekund
        setInterval(fetchUnreadCount, 60000);
    }
});