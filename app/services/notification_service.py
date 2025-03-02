from datetime import datetime, timedelta
from app.models.notification import Notification
from app.models.advertisement import Advertisement
from app.models.ad_carrier import AdCarrier
from app.extensions import db

def generate_ad_expiry_notifications(days_before=7):
    """
    Generuje powiadomienia o reklamach, których termin zakończenia zbliża się.
    
    Args:
        days_before: Liczba dni przed zakończeniem, kiedy ma zostać wygenerowane powiadomienie
    
    Returns:
        int: Liczba wygenerowanych powiadomień
    """
    today = datetime.utcnow().date()
    target_date = today + timedelta(days=days_before)
    
    # Znajdź reklamy, które kończą się za określoną liczbę dni
    ads = Advertisement.query.filter_by(status='active').filter(
        Advertisement.end_date == target_date
    ).all()
    
    count = 0
    for ad in ads:
        # Sprawdź, czy powiadomienie dla tej reklamy już istnieje
        existing = Notification.query.filter(
            Notification.target_url == f"/ads/{ad.id}",
            Notification.type == 'warning',
            Notification.is_read == False
        ).first()
        
        if not existing:
            Notification.create_ad_expiry_notification(ad)
            count += 1
    
    return count

def generate_carrier_inspection_notifications(days_since_last_inspection=30):
    """
    Generuje powiadomienia o nośnikach, które powinny być poddane inspekcji.
    
    Args:
        days_since_last_inspection: Liczba dni od ostatniej inspekcji, po której generowane jest powiadomienie
    
    Returns:
        int: Liczba wygenerowanych powiadomień
    """
    today = datetime.utcnow().date()
    threshold_date = today - timedelta(days=days_since_last_inspection)
    
    # Znajdź nośniki, które nie miały inspekcji od określonego czasu
    carriers = AdCarrier.query.filter_by(status='active').filter(
        (AdCarrier.last_inspection_date <= threshold_date) |
        (AdCarrier.last_inspection_date == None)
    ).all()
    
    count = 0
    for carrier in carriers:
        # Sprawdź, czy powiadomienie dla tego nośnika już istnieje
        existing = Notification.query.filter(
            Notification.target_url == f"/carriers/{carrier.id}",
            Notification.type == 'info',
            Notification.is_read == False
        ).first()
        
        if not existing:
            Notification.create_carrier_inspection_notification(carrier)
            count += 1
    
    return count

def check_notifications():
    """
    Sprawdza i generuje wszystkie typy powiadomień.
    
    Returns:
        dict: Statystyki wygenerowanych powiadomień
    """
    stats = {
        'ad_expiry': generate_ad_expiry_notifications(),
        'carrier_inspection': generate_carrier_inspection_notifications()
    }
    
    return stats