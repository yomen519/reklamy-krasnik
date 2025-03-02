# app/services/image_service.py
import os
import uuid
import logging
from datetime import datetime
from werkzeug.utils import secure_filename
from PIL import Image, ExifTags
from flask import current_app


def allowed_file(filename):
    """Sprawdza, czy rozszerzenie pliku jest dozwolone."""
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_image(file, max_size=(1200, 1200), quality=85):
    """
    Zapisuje zdjęcie, tworzy miniaturę i ekstrahuje metadane EXIF.
    Optymalizuje rozmiar oryginalnego zdjęcia.

    Args:
        file: Obiekt pliku z request.files
        max_size: Maksymalny rozmiar w pikselach (szerokość, wysokość)
        quality: Jakość kompresji JPEG (1-100)

    Returns:
        dict: Słownik z informacjami o zapisanym pliku lub None w przypadku błędu
    """
    if not file or not allowed_file(file.filename):
        logging.warning(f"Nieprawidłowy plik: {file.filename if file else 'None'}")
        return None

    try:
        # Tworzymy bezpieczną unikalną nazwę pliku
        original_name = file.filename
        filename = secure_filename(f"{uuid.uuid4().hex}_{original_name}")

        # Ścieżki do plików
        original_folder = os.path.join(current_app.root_path, current_app.config['ORIGINAL_FOLDER'])
        thumbnail_folder = os.path.join(current_app.root_path, current_app.config['THUMBNAIL_FOLDER'])

        # Upewnij się, że katalogi istnieją
        os.makedirs(original_folder, exist_ok=True)
        os.makedirs(thumbnail_folder, exist_ok=True)

        # Tworzymy ścieżki do plików
        original_path = os.path.join(original_folder, filename)
        thumbnail_path = os.path.join(thumbnail_folder, filename)
        temp_path = os.path.join(original_folder, f"temp_{filename}")

        # Zapisujemy tymczasowo oryginalny plik
        file.save(temp_path)

        # Dane do zwrotu
        result = {
            'filename': filename,
            'original_filename': original_name,
            'taken_at': None,
            'gps_latitude': None,
            'gps_longitude': None
        }

        # Tworzymy miniaturę i ekstrahujemy EXIF
        try:
            with Image.open(temp_path) as img:
                # Ekstrahujemy EXIF przed jakąkolwiek modyfikacją
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif():
                    exif = {
                        ExifTags.TAGS[k]: v
                        for k, v in img._getexif().items()
                        if k in ExifTags.TAGS
                    }

                    # Pobieramy datę wykonania zdjęcia
                    if 'DateTimeOriginal' in exif:
                        try:
                            result['taken_at'] = datetime.strptime(
                                exif['DateTimeOriginal'],
                                '%Y:%m:%d %H:%M:%S'
                            )
                        except Exception as e:
                            logging.error(f"Błąd parsowania daty EXIF: {str(e)}")

                    # Pobieramy dane GPS
                    if 'GPSInfo' in exif:
                        gps_info = {}
                        for key in exif['GPSInfo'].keys():
                            decode = ExifTags.GPSTAGS.get(key, key)
                            gps_info[decode] = exif['GPSInfo'][key]

                        # Konwertujemy współrzędne
                        if 'GPSLatitude' in gps_info and 'GPSLongitude' in gps_info:
                            try:
                                lat = _convert_to_degrees(gps_info['GPSLatitude'])
                                lon = _convert_to_degrees(gps_info['GPSLongitude'])

                                # Sprawdzamy referencje N/S i E/W
                                if gps_info.get('GPSLatitudeRef') == 'S':
                                    lat = -lat
                                if gps_info.get('GPSLongitudeRef') == 'W':
                                    lon = -lon

                                result['gps_latitude'] = lat
                                result['gps_longitude'] = lon
                            except Exception as e:
                                logging.error(f"Błąd konwersji danych GPS: {str(e)}")

                # Optymalizacja oryginalnego zdjęcia
                img.thumbnail(max_size, Image.LANCZOS)
                
                # Określamy format wyjściowy
                save_format = 'JPEG' if img.format in ('JPEG', 'JPG') else img.format
                
                # Zapisujemy zoptymalizowany oryginał
                if save_format == 'JPEG':
                    img.save(original_path, format=save_format, quality=quality, optimize=True)
                else:
                    img.save(original_path, format=save_format)
                
                # Tworzymy miniaturę (jeszcze mniejszą)
                img.thumbnail((200, 200), Image.LANCZOS)
                if save_format == 'JPEG':
                    img.save(thumbnail_path, format=save_format, quality=85, optimize=True)
                else:
                    img.save(thumbnail_path, format=save_format)
                
                # Usuwamy tymczasowy plik
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                
                return result
        except Exception as e:
            # W przypadku błędu usuwamy pliki
            if os.path.exists(temp_path):
                os.remove(temp_path)
            if os.path.exists(original_path):
                os.remove(original_path)
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
            logging.error(f"Błąd przetwarzania zdjęcia: {str(e)}")
            return None
    except Exception as e:
        logging.error(f"Ogólny błąd podczas zapisywania zdjęcia: {str(e)}")
        return None


def _convert_to_degrees(value):
    """
    Konwertuje współrzędne GPS z formatu EXIF do stopni.

    Args:
        value: Krotka (stopnie, minuty, sekundy)

    Returns:
        float: Współrzędne w stopniach dziesiętnych
    """
    d = float(value[0])
    m = float(value[1])
    s = float(value[2])

    return d + (m / 60.0) + (s / 3600.0)

def find_nearest_carrier(lat, lon, max_distance=0.1):
    """
    Znajduje najbliższy nośnik reklamowy dla danych współrzędnych GPS.

    Args:
        lat: Szerokość geograficzna
        lon: Długość geograficzna
        max_distance: Maksymalna odległość w stopniach (ok. 11 km dla 0.1)

    Returns:
        AdCarrier: Najbliższy nośnik lub None
    """
    from app.models.ad_carrier import AdCarrier
    from app.models.location import Location
    from sqlalchemy import func

    # Najpierw znajdujemy wszystkie aktywne lokalizacje w okolicy
    locations = Location.query.filter_by(active=True).all()

    nearest = None
    min_distance = float('inf')

    for location in locations:
        if location.lat is None or location.lon is None:
            continue

        # Obliczamy odległość (uproszczona, dla małych obszarów)
        dist = ((location.lat - lat) ** 2 + (location.lon - lon) ** 2) ** 0.5

        if dist < min_distance and dist < max_distance:
            min_distance = dist

            # Pobieramy aktywne nośniki z tej lokalizacji
            carriers = AdCarrier.query.filter_by(location_id=location.id, status='active').all()
            if carriers:
                nearest = carriers[0]  # Bierzemy pierwszy aktywny nośnik

    return nearest
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
        logging.warning(f"Brak współrzędnych GPS: lat={latitude}, lon={longitude}")
        return None, None, 0
    
    logging.info(f"Szukam reklamy dla współrzędnych: lat={latitude}, lon={longitude}")
    
    today = datetime.utcnow().date()
    if taken_at and isinstance(taken_at, datetime):
        photo_date = taken_at.date()
    else:
        photo_date = today
        
    logging.info(f"Używam daty zdjęcia: {photo_date}")
    
    # Szukamy wszystkich aktywnych lokalizacji
    locations = Location.query.filter_by(active=True).all()
    logging.info(f"Znaleziono {len(locations)} aktywnych lokalizacji")
    
    nearest_ad = None
    min_distance = float('inf')
    confidence = 0
    
    for location in locations:
        if location.lat is None or location.lon is None:
            logging.warning(f"Lokalizacja {location.id}: {location.name} nie ma współrzędnych GPS")
            continue
        
        # Obliczamy odległość w metrach
        try:
            distance = calculate_distance(
                float(latitude), float(longitude),
                float(location.lat), float(location.lon)
            )
            
            logging.info(f"Lokalizacja {location.id}: {location.name}, odległość: {distance:.2f}m")
            
            if distance < min_distance and distance <= max_distance:
                # Sprawdzamy nośniki w tej lokalizacji
                carriers = AdCarrier.query.filter_by(location_id=location.id, status='active').all()
                logging.info(f"Znaleziono {len(carriers)} aktywnych nośników w lokalizacji {location.id}")
                
                for carrier in carriers:
                    # Szukamy aktywnych reklam dla tego nośnika w dniu wykonania zdjęcia
                    ads = Advertisement.query.filter(
                        Advertisement.carrier_id == carrier.id,
                        Advertisement.start_date <= photo_date,
                        Advertisement.end_date >= photo_date
                    ).all()
                    
                    if ads:
                        logging.info(f"Znaleziono {len(ads)} aktywnych reklam na nośniku {carrier.id}")
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
                            logging.info(f"Wybrano reklamę {nearest_ad.id}: {nearest_ad.title}, pewność: {confidence:.2f}")
                        else:
                            # Jeśli jest więcej reklam, wybieramy tę, która kończy się najwcześniej
                            # Założenie: operatorzy częściej robią zdjęcia reklam, które wkrótce będą wymieniane
                            sorted_ads = sorted(ads, key=lambda x: x.end_date)
                            nearest_ad = sorted_ads[0]
                            confidence = confidence_score * 0.9  # Nieco niższa pewność przy wielu reklamach
                            logging.info(f"Wybrano jedną z {len(ads)} reklam: {nearest_ad.id}: {nearest_ad.title}, pewność: {confidence:.2f}")
        
        except (ValueError, TypeError) as e:
            logging.error(f"Błąd podczas obliczania odległości dla lokalizacji {location.id}: {str(e)}")
            continue
    
    if nearest_ad:
        logging.info(f"Ostatecznie wybrano reklamę {nearest_ad.id} w odległości {min_distance:.2f}m z pewnością {confidence:.2f}")
    else:
        logging.warning(f"Nie znaleziono pasującej reklamy w promieniu {max_distance}m")
    
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
def batch_process_images(files, confidence_threshold=0.7):
    """
    Przetwarza wiele plików zdjęć, przypisując je automatycznie do reklam na podstawie GPS.
    
    Args:
        files: Lista obiektów plików z request.files
        confidence_threshold: Próg pewności dla automatycznego przypisania
        
    Returns:
        dict: Statystyki przetwarzania zdjęć
    """
    from app.models.photo import Photo
    from app.extensions import db
    from datetime import datetime
    import logging
    
    results = {
        'total': len(files),
        'processed': 0,
        'auto_assigned': 0,
        'unassigned': 0,
        'errors': 0,
        'assignments': []
    }
    
    unassigned_photos = []
    
    for file in files:
        if not file or not allowed_file(file.filename):
            results['errors'] += 1
            continue
        
        try:
            # Zapisujemy zdjęcie i pobieramy metadane
            image_data = save_image(file)
            if not image_data:
                results['errors'] += 1
                continue
            
            results['processed'] += 1
            
            # Próbujemy znaleźć najbliższą reklamę na podstawie GPS
            latitude = image_data.get('gps_latitude')
            longitude = image_data.get('gps_longitude')
            taken_at = image_data.get('taken_at')
            
            ad, distance, confidence = find_nearest_advertisement(
                latitude, longitude, taken_at=taken_at
            )
            
            # Jeśli znaleźliśmy reklamę z wystarczającą pewnością, przypisujemy zdjęcie
            if ad and confidence >= confidence_threshold:
                photo = Photo(
                    advertisement_id=ad.id,
                    filename=image_data['filename'],
                    original_filename=image_data['original_filename'],
                    taken_at=taken_at,
                    gps_latitude=latitude,
                    gps_longitude=longitude,
                    upload_date=datetime.utcnow()
                )
                db.session.add(photo)
                results['auto_assigned'] += 1
                results['assignments'].append({
                    'filename': image_data['original_filename'],
                    'ad_id': ad.id,
                    'ad_title': ad.title,
                    'distance': distance,
                    'confidence': confidence
                })
            else:
                # Zapisujemy informacje o zdjęciu bez przypisania, żeby użytkownik mógł przypisać ręcznie
                unassigned_photos.append(image_data)
                results['unassigned'] += 1
        except Exception as e:
            logging.error(f"Błąd przetwarzania zdjęcia {file.filename}: {str(e)}")
            results['errors'] += 1
    
    # Zapisujemy zmiany w bazie danych
    if results['auto_assigned'] > 0:
        db.session.commit()
    
    # Zwracamy wyniki przetwarzania
    return results, unassigned_photos
from app.models.photo import Photo