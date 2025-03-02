from flask import Blueprint, render_template, request, current_app

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Główny widok z mapą."""
    # Sprawdzamy, czy są parametry lokalizacji
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    zoom = request.args.get('zoom', 13)
    
    # Pobieramy domyślne centrum mapy z konfiguracji
    default_center = current_app.config.get('DEFAULT_MAP_CENTER', [50.946954, 22.221636])
    default_zoom = current_app.config.get('DEFAULT_MAP_ZOOM', 13)
    
    # Używamy parametrów lub wartości domyślnych
    try:
        if lat and lon:
            map_center = [float(lat), float(lon)]
        else:
            map_center = default_center
        
        map_zoom = int(zoom) if zoom else default_zoom
    except (ValueError, TypeError):
        map_center = default_center
        map_zoom = default_zoom
    
    return render_template('index.html', 
                           map_center=map_center, 
                           map_zoom=map_zoom)