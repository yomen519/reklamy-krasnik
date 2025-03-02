from datetime import datetime
from app.extensions import db


class Advertisement(db.Model):
    """Model reprezentujący reklamę."""
    __tablename__ = 'advertisements'

    id = db.Column(db.Integer, primary_key=True)
    carrier_id = db.Column(db.Integer, db.ForeignKey('ad_carriers.id'), nullable=False)
    side = db.Column(db.Integer, default=1)  # Strona nośnika (1 lub 2)
    title = db.Column(db.String(100))
    client = db.Column(db.String(100))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='active')  # 'scheduled', 'active', 'finished'
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacje
    carrier = db.relationship('AdCarrier', back_populates='advertisements')
    photos = db.relationship('Photo', back_populates='advertisement', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Advertisement {self.id} for {self.carrier_id}>'

    def to_dict(self):
        """Konwertuje model do słownika do użycia w API."""
        return {
            'id': self.id,
            'carrier_id': self.carrier_id,
            'side': self.side,
            'title': self.title,
            'client': self.client,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'notes': self.notes,
            'photos': [photo.to_dict() for photo in self.photos]
        }

    @property
    def is_active(self):
        """Sprawdza, czy reklama jest aktywna (w okresie ekspozycji)."""
        today = datetime.utcnow().date()
        return self.start_date <= today <= self.end_date

    @property
    def days_remaining(self):
        """Zwraca liczbę dni pozostałych do końca ekspozycji."""
        today = datetime.utcnow().date()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days

    @property
    def thumbnail(self):
        """Zwraca miniaturkę pierwszego zdjęcia lub None."""
        if self.photos and len(self.photos) > 0:
            return self.photos[0].thumbnail_url
        return None
        
    @property
    def status_pl(self):
        """Zwraca polski opis statusu."""
        status_map = {
            'scheduled': 'Zaplanowana',
            'active': 'Aktywna',
            'finished': 'Zakończona'
        }
        return status_map.get(self.status, self.status)