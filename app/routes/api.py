from flask import Blueprint, jsonify, request
from app.models.location import Location
from app.models.ad_carrier import AdCarrier
from app.models.advertisement import Advertisement
from datetime import datetime
import logging

api_bp = Blueprint('api', __name__)

@api_bp.route('/map-data')
def map_data():
    """Zwraca dane dla mapy w formacie GeoJSON."""
    carrier_type = request.args.get('type')
    status = request.args.get('status')
    
    # Zawsze pobieramy stałe lokalizacje
    permanent_locations = Location.query.filter_by(permanent=True, active=True).all()
    
    # Pozostałe lokalizacje (opcjonalnie, wg filtrów)
    query = Location.query.filter_by(permanent=False, active=True)
    other_locations = query.all()
    
    # Łączymy obie listy
    all_locations = permanent_locations + other_locations
    
    features = []
    
    for location in all_locations:
        # Sprawdzamy czy mamy prawidłowe współrzędne
        try:
            if location.lat is None or location.lon is None:
                logging.warning(
                    f"Lokalizacja {location.id}: {location.name} ma nieprawidłowe współrzędne: {location.coordinates}")
                continue
            
            # Pobieramy aktywne nośniki dla lokalizacji
            carriers_query = location.carriers
            
            # Filtrowanie nośników
            if carrier_type:
                carriers_query = carriers_query.filter_by(carrier_type=carrier_type)
            if status:
                carriers_query = carriers_query.filter_by(status=status)
            
            carriers = carriers_query.all()
            
            if not carriers and not location.permanent:
                continue
            
            # Tworzymy dane dla markera
            carriers_data = []
            for carrier in carriers:
                # Pobieramy aktywne reklamy dla nośnika
                today = datetime.utcnow().date()
                advertisements = carrier.advertisements.filter(
                    Advertisement.start_date <= today,
                    Advertisement.end_date >= today
                ).all()
                
                ads_data = []
                for ad in advertisements:
                    ad_data = ad.to_dict()
                    # Dodajemy zdjęcia
                    ad_data['photos'] = [
                        {
                            'id': photo.id,
                            'thumbnail_url': photo.thumbnail_url,
                            'original_url': photo.original_url
                        } 
                        for photo in ad.photos
                    ]
                    ads_data.append(ad_data)
                
                carriers_data.append({
                    'id': carrier.id,
                    'type': carrier.carrier_type,
                    'sides': carrier.sides,
                    'dimensions': carrier.dimensions,
                    'status': carrier.status,
                    'technical_condition': carrier.technical_condition,
                    'advertisements': ads_data
                })
            
            # Sprawdzanie i konwersja współrzędnych na float
            lon = float(location.lon)
            lat = float(location.lat)
            
            # Tworzymy GeoJSON Feature
            feature = {
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [lon, lat]
                },
                'properties': {
                    'id': location.id,
                    'name': location.name,
                    'address': location.address,
                    'permanent': location.permanent,
                    'carriers': carriers_data,
                    'lat': lat,
                    'lon': lon
                }
            }
            
            features.append(feature)
        except (TypeError, ValueError) as e:
            logging.error(
                f"Błąd przy przetwarzaniu lokalizacji {location.id}: {location.name}, współrzędne: {location.coordinates}. Błąd: {str(e)}")
            continue
    
    # Tworzymy GeoJSON FeatureCollection
    geojson = {
        'type': 'FeatureCollection',
        'features': features
    }
    
    return jsonify(geojson)