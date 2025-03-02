from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.models.notification import Notification
from app.services.notification_service import check_notifications
from app.extensions import db

notification_bp = Blueprint('notification', __name__)

@notification_bp.route('/')
def index():
    """Strona główna powiadomień."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Pobierz powiadomienia z paginacją
    notifications = Notification.query.order_by(
        Notification.is_read.asc(),
        Notification.created_at.desc()
    ).paginate(page=page, per_page=per_page)
    
    return render_template('notifications/index.html', notifications=notifications)

@notification_bp.route('/check')
def check():
    """Ręczne sprawdzenie i wygenerowanie powiadomień."""
    stats = check_notifications()
    
    total = sum(stats.values())
    if total > 0:
        message = f"Wygenerowano {total} nowych powiadomień."
    else:
        message = "Nie znaleziono żadnych nowych powiadomień."
    
    return redirect(url_for('notification.index', message=message))

@notification_bp.route('/mark-read/<int:notification_id>', methods=['POST'])
def mark_read(notification_id):
    """Oznacza powiadomienie jako przeczytane."""
    notification = Notification.query.get_or_404(notification_id)
    notification.is_read = True
    db.session.commit()
    
    # Jeśli to żądanie AJAX, zwróć JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    
    # W przeciwnym razie przekieruj z powrotem
    return redirect(url_for('notification.index'))

@notification_bp.route('/mark-all-read', methods=['POST'])
def mark_all_read():
    """Oznacza wszystkie powiadomienia jako przeczytane."""
    Notification.query.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    
    # Jeśli to żądanie AJAX, zwróć JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    
    # W przeciwnym razie przekieruj z powrotem
    return redirect(url_for('notification.index'))

@notification_bp.route('/api/unread-count')
def api_unread_count():
    """Zwraca liczbę nieprzeczytanych powiadomień jako JSON."""
    count = Notification.get_unread_count()
    return jsonify({'count': count})

@notification_bp.route('/api/recent')
def api_recent():
    """Zwraca listę najnowszych powiadomień jako JSON."""
    limit = request.args.get('limit', 5, type=int)
    notifications = [n.to_dict() for n in Notification.get_recent(limit)]
    return jsonify({'notifications': notifications})