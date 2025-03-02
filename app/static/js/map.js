// Inicjalizacja mapy
document.addEventListener('DOMContentLoaded', function() {
    // Pobierz centrum i zoom z danych przekazanych z serwera lub użyj domyślnych
    const MAP_CENTER = typeof mapCenter !== 'undefined' ? mapCenter : [50.928, 22.227]; // domyślnie Kraśnik
    const MAP_ZOOM = typeof mapZoom !== 'undefined' ? mapZoom : 13;
    
    // Inicjalizacja mapy
    const map = L.map('map').setView(MAP_CENTER, MAP_ZOOM);
    
    // Dodajemy warstwę OpenStreetMap
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    
    // Inicjalizacja klastrów markerów
    const markers = L.markerClusterGroup();
    map.addLayer(markers);
    
    // Ikony dla różnych typów nośników
    const carrierIcons = {
        'citylight': L.icon({
            iconUrl: '/static/img/citylight-icon.png',
            iconSize: [32, 32],
            iconAnchor: [16, 32],
            popupAnchor: [0, -32],
            // Fallback w przypadku braku ikony
            _fallback: true,
            _createIcon: function(oldIcon) {
                const div = document.createElement('div');
                div.innerHTML = '<div style="width: 32px; height: 32px; background-color: #3388ff; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-weight: bold;">C</div>';
                return div.firstChild;
            }
        }),
        'baner': L.icon({
            iconUrl: '/static/img/banner-icon.png',
            iconSize: [32, 32],
            iconAnchor: [16, 32],
            popupAnchor: [0, -32],
            // Fallback w przypadku braku ikony
            _fallback: true,
            _createIcon: function(oldIcon) {
                const div = document.createElement('div');
                div.innerHTML = '<div style="width: 32px; height: 32px; background-color: #e74c3c; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-weight: bold;">B</div>';
                return div.firstChild;
            }
        }),
        'default': L.icon({
            iconUrl: '/static/img/default-icon.png',
            iconSize: [32, 32],
            iconAnchor: [16, 32],
            popupAnchor: [0, -32],
            // Fallback w przypadku braku ikony
            _fallback: true,
            _createIcon: function(oldIcon) {
                const div = document.createElement('div');
                div.innerHTML = '<div style="width: 32px; height: 32px; background-color: #27ae60; border-radius: 50%; display: flex; justify-content: center; align-items: center; color: white; font-weight: bold;">L</div>';
                return div.firstChild;
            }
        })
    };
    
    // Funkcja zwracająca etykietę dla statusu
    function getStatusLabel(status) {
        const statusLabels = {
            'active': 'Aktywny',
            'damaged': 'Uszkodzony',
            'repair_needed': 'Wymaga naprawy',
            'inactive': 'Nieaktywny'
        };
        return statusLabels[status] || status;
    }
    
    // Funkcja do tworzenia zawartości popupu
    function createPopupContent(feature) {
        const props = feature.properties;
        let content = `<div class="map-popup">
            <h5>${props.name}</h5>
            <p>${props.address || ''}</p>`;
        
        // Dodajemy sekcje dla każdego nośnika
        for (const carrier of props.carriers) {
            content += `<div class="carrier-info mt-2">
                <h6>${carrier.type === 'citylight' ? 'Citylight' : 'Baner'} 
                    (${carrier.sides} ${carrier.sides > 1 ? 'strony' : 'strona'})</h6>
                <div class="d-flex justify-content-between mb-1">
                    <small>Status: ${getStatusLabel(carrier.status)}</small>
                    <a href="/carriers/${carrier.id}" class="small">Szczegóły</a>
                </div>`;
            
            // Dodajemy karuzele dla każdej aktywnej reklamy
            if (carrier.advertisements && carrier.advertisements.length > 0) {
                content += `<div class="advertisements-container">`;
                
                for (const ad of carrier.advertisements) {
                    content += `<div class="advertisement mb-2">
                        <div class="d-flex justify-content-between align-items-center">
                            <span>${ad.title || 'Reklama'} (strona ${ad.side})</span>
                            <div>
                                <a href="/ads/${ad.id}" class="btn btn-sm btn-outline-primary">Edytuj</a>
                                <a href="/ads/${ad.id}/photos/add?from_map=1&lat=${props.lat}&lon=${props.lon}" class="btn btn-sm btn-outline-success">+ Zdjęcie</a>
                            </div>
                        </div>`;
                    
                    // Dodajemy karuzele zdjęć, jeśli są
                    if (ad.photos && ad.photos.length > 0) {
                        content += `<div class="swiper-container ad-photos-swiper mt-2" id="swiper-${ad.id}">
                            <div class="swiper-wrapper">`;
                        
                        for (const photo of ad.photos) {
                            content += `<div class="swiper-slide">
                                <a href="${photo.original_url}" target="_blank">
                                    <img src="${photo.thumbnail_url}" class="img-fluid" alt="Zdjęcie reklamy">
                                </a>
                                <a href="/photos/${photo.id}/delete?from_map=1&lat=${props.lat}&lon=${props.lon}" 
                                   class="btn btn-sm btn-danger delete-photo"
                                   onclick="return confirm('Czy na pewno chcesz usunąć to zdjęcie?')">Usuń</a>
                            </div>`;
                        }
                        
                        content += `</div>
                            <div class="swiper-pagination"></div>
                            <div class="swiper-button-next"></div>
                            <div class="swiper-button-prev"></div>
                        </div>`;
                    } else {
                        content += `<p class="small text-muted mt-1">Brak zdjęć</p>`;
                    }
                    
                    content += `</div>`;
                }
                
                content += `</div>`;
            } else {
                content += `<p class="small text-muted">Brak aktywnych reklam</p>`;
                content += `<a href="/ads/add?carrier_id=${carrier.id}" class="btn btn-sm btn-outline-primary">Dodaj reklamę</a>`;
            }
            
            content += `</div>`;
        }
        
        content += `</div>`;
        return content;
    }
    
    // Funkcja do inicjalizacji karuzeli po otwarciu popupu
    function initSwiper(feature) {
        for (const carrier of feature.properties.carriers) {
            if (carrier.advertisements) {
                for (const ad of carrier.advertisements) {
                    if (ad.photos && ad.photos.length > 0) {
                        new Swiper(`#swiper-${ad.id}`, {
                            slidesPerView: 1,
                            spaceBetween: 10,
                            pagination: {
                                el: '.swiper-pagination',
                                clickable: true
                            },
                            navigation: {
                                nextEl: '.swiper-button-next',
                                prevEl: '.swiper-button-prev'
                            }
                        });
                    }
                }
            }
        }
    }
    
    // Ładowanie danych dla mapy
    function loadMapData(filters = {}) {
        // Budujemy URL z filtrami
        let url = '/api/map-data';
        const params = new URLSearchParams();
        
        if (filters.type) {
            params.append('type', filters.type);
        }
        if (filters.status) {
            params.append('status', filters.status);
        }
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        // Pobieramy dane
        fetch(url)
            .then(response => response.json())
            .then(data => {
                // Czyścimy istniejące markery
                markers.clearLayers();
                
                // Dodajemy nowe markery
                L.geoJSON(data, {
                    pointToLayer: function(feature, latlng) {
                        // Wybieramy ikonę na podstawie typu pierwszego nośnika
                        let iconType = 'default';
                        if (feature.properties.carriers && feature.properties.carriers.length > 0) {
                            iconType = feature.properties.carriers[0].type;
                        }
                        
                        const icon = carrierIcons[iconType] || carrierIcons['default'];
                        return L.marker(latlng, { icon: icon });
                    },
                    onEachFeature: function(feature, layer) {
                        // Dodajemy popup
                        layer.bindPopup(createPopupContent(feature));
                        
                        // Inicjalizujemy karuzelę po otwarciu popupu
                        layer.on('popupopen', function() {
                            initSwiper(feature);
                        });
                    }
                }).addTo(markers);
            })
            .catch(error => {
                console.error('Błąd ładowania danych dla mapy:', error);
                alert('Nie udało się załadować danych dla mapy. Spróbuj odświeżyć stronę.');
            });
    }
    
    // Obsługa filtrowania
    const filterForm = document.getElementById('map-filter-form');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(filterForm);
            const filters = {
                type: formData.get('type'),
                status: formData.get('status')
            };
            
            loadMapData(filters);
        });
        
        // Przycisk resetowania filtrów
        const resetButton = document.getElementById('reset-filters');
        if (resetButton) {
            resetButton.addEventListener('click', function() {
                filterForm.reset();
                loadMapData();
            });
        }
    }
    
    // Inicjalne załadowanie danych
    loadMapData();
    
    // Eksport funkcji i obiektów do globalnego zakresu
    window.mapApi = {
        map: map,
        markers: markers,
        loadMapData: loadMapData
    };
});

// Style CSS dla popupu i karuzeli
const mapStyles = `
.map-popup {
    max-width: 300px;
    max-height: 400px;
    overflow-y: auto;
}

.ad-photos-swiper {
    width: 100%;
    height: 150px;
    margin-bottom: 10px;
}

.swiper-slide img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.swiper-button-next, .swiper-button-prev {
    color: #007bff;
    transform: scale(0.7);
}

.delete-photo {
    position: absolute;
    bottom: 5px;
    right: 5px;
    font-size: 0.7rem;
    padding: 2px 5px;
    z-index: 10;
}
`;

// Dodajemy style do dokumentu
document.addEventListener('DOMContentLoaded', function() {
    const styleElement = document.createElement('style');
    styleElement.textContent = mapStyles;
    document.head.appendChild(styleElement);
});