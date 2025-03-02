from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from datetime import datetime
import math
import logging

def geocode_address(address):
    """
    Konwertuje adres tekstowy na współrzędne geograficzne.
    
    Args:
        address: Adres tekstowy (np. "ul. Lubelska, Kraśnik")
        
    Returns:
        str: Współrzędne w formacie "lat,lon" lub None w przypadku błędu
    """
    try:
        geolocator = Nominatim(user_agent="reklamy_krasnik")
        location = geolocator.geocode(address)
        if location:
            return f"{location.latitude},{location.longitude}"
        return None
    except (GeocoderTimedOut, GeocoderServiceError):
        return None

def reverse_geocode(lat, lon):
    """
    Konwertuje współrzędne geograficzne na adres.
    
    Args:
        lat: Szerokość geograficzna
        lon: Długość geograficzna
        
    Returns:
        str: Adres tekstowy lub None w przypadku błędu
    """
    try:
        geolocator = Nominatim(user_agent="reklamy_krasnik")
        location = geolocator.reverse(f"{lat}, {lon}")
        if location:
            return location.address
        return None
    except (GeocoderTimedOut, GeocoderServiceError):
        return None

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Oblicza odległość między dwoma punktami na podstawie współrzędnych geograficznych.
    Wykorzystuje wzór haversine do dokładnych obliczeń na sferze.
    
    Args:
        lat1: Szerokość geograficzna punktu 1
        lon1: Długość geograficzna punktu 1
        lat2: Szerokość geograficzna punktu 2
        lon2: Długość geograficzna punktu 2
        
    Returns:
        float: Odległość w metrach
    """
    # Konwersja stopni na radiany
    try:
        lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
        
        # Wzór haversine
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371000  # Promień Ziemi w metrach
        
        return c * r
    except (ValueError, TypeError) as e:
        logging.error(f"Błąd przy obliczaniu odległości: {str(e)}")
        return float('inf')

def find_nearest_advertisement(latitude, longitude, max_distance=100, taken_at=None):
    """
    Znajduje najbliższą reklamę do podanych współrzędnych GPS.
    
    Args:
        latitude: Szerokość geograficzna
        longitude: Długość geograficzna
        max_distance: Maksymalny dystans w metrach (domyślnie 100m)
        taken_at: Data wykonania zdjęcia, jeśli dostępna
        
    Returns:
        tuple: (advertisement, distance, confidence) lub (None, None, 0) jeśli nie znaleziono
    """
    from app.models.location import Location
    from app.models.ad_carrier import AdCarrier
    from app.models.advertisement import Advertisement
    
    if not latitude or not longitude:
        return None, None, 0
    
    today = datetime.utcnow().date()
    if taken_at and isinstance(taken_at, datetime):
        photo_date = taken_at.date()
    else:
        photo_date = today
    
    # Szukamy wszystkich aktywnych lokalizacji
    locations = Location.query.filter_by(active=True).all()
    
    nearest_ad = None
    min_distance = float('inf')
    confidence = 0
    
    for location in locations:
        if location.lat is None or location.lon is None:
            continue
        
        # Obliczamy odległość w metrach
        try:
            distance = calculate_distance(
                float(latitude), float(longitude),
                float(location.lat), float(location.lon)
            )
            
            if distance < min_distance and distance <= max_distance:
                # Sprawdzamy nośniki w tej lokalizacji
                carriers = AdCarrier.query.filter_by(location_id=location.id, status='active').all()
                
                for carrier in carriers:
                    # Szukamy aktywnych reklam dla tego nośnika w dniu wykonania zdjęcia
                    ads = Advertisement.query.filter(
                        Advertisement.carrier_id == carrier.id,
                        Advertisement.start_date <= photo_date,
                        Advertisement.end_date >= photo_date
                    ).all()
                    
                    if ads:
                        min_distance = distance
                        
                        # Obliczamy pewność na podstawie odległości
                        # Im bliżej, tym większa pewność
                        # 10m = 95%, 50m = 80%, 100m = 60%
                        if distance < 10:
                            confidence_score = 0.95
                        elif distance < 50:
                            confidence_score = 0.8
                        else:
                            confidence_score = 0.6
                        
                        # Jeśli jest tylko jedna reklama, zwracamy ją
                        if len(ads) == 1:
                            nearest_ad = ads[0]
                            confidence = confidence_score
                        else:
                            # Jeśli jest więcej reklam, wybieramy tę, która kończy się najwcześniej
                            # Założenie: operatorzy częściej robią zdjęcia reklam, które wkrótce będą wymieniane
                            sorted_ads = sorted(ads, key=lambda x: x.end_date)
                            nearest_ad = sorted_ads[0]
                            confidence = confidence_score * 0.9  # Nieco niższa pewność przy wielu reklamach
        
        except (ValueError, TypeError) as e:
            logging.error(f"Błąd podczas obliczania odległości: {str(e)}")
            continue
    
    return nearest_ad, min_distance, confidence

def find_nearest_carrier(latitude, longitude, max_distance=100):
    """
    Znajduje najbliższy nośnik reklamowy dla danych współrzędnych GPS.
    
    Args:
        latitude: Szerokość geograficzna
        longitude: Długość geograficzna
        max_distance: Maksymalny dystans w metrach (domyślnie 100m)
        
    Returns:
        tuple: (AdCarrier, distance) lub (None, None) jeśli nie znaleziono
    """
    from app.models.location import Location
    from app.models.ad_carrier import AdCarrier
    
    if not latitude or not longitude:
        return None, None
    
    # Szukamy wszystkich aktywnych lokalizacji
    locations = Location.query.filter_by(active=True).all()
    
    nearest_carrier = None
    min_distance = float('inf')
    
    for location in locations:
        if location.lat is None or location.lon is None:
            continue
        
        # Obliczamy odległość w metrach
        try:
            distance = calculate_distance(
                float(latitude), float(longitude),
                float(location.lat), float(location.lon)
            )
            
            if distance < min_distance and distance <= max_distance:
                # Pobieramy aktywne nośniki z tej lokalizacji
                carriers = AdCarrier.query.filter_by(location_id=location.id, status='active').all()
                
                if carriers:
                    min_distance = distance
                    nearest_carrier = carriers[0]  # Bierzemy pierwszy aktywny nośnik
        
        except (ValueError, TypeError) as e:
            logging.error(f"Błąd podczas obliczania odległości: {str(e)}")
            continue
    
    return nearest_carrier, min_distance