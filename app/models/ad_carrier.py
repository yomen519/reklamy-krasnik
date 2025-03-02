from datetime import datetime
from app.extensions import db


class AdCarrier(db.Model):
    """Model reprezentujący nośnik reklamowy (citylight, baner)."""
    __tablename__ = 'ad_carriers'

    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('locations.id'), nullable=False)
    carrier_type = db.Column(db.String(20), nullable=False)  # 'citylight' lub 'baner'
    sides = db.Column(db.Integer, default=1)  # Liczba stron (1 lub 2)
    dimensions = db.Column(db.String(50))  # Wymiary w cm
    technical_condition = db.Column(db.Text)
    installation_date = db.Column(db.Date)
    last_inspection_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')  # 'active', 'damaged', 'repair_needed', 'inactive'
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacje
    location = db.relationship('Location', back_populates='carriers')
    advertisements = db.relationship('Advertisement', back_populates='carrier', lazy='dynamic')

    def __repr__(self):
        return f'<AdCarrier {self.id} {self.carrier_type}>'

    def to_dict(self):
        """Konwertuje model do słownika do użycia w API."""
        return {
            'id': self.id,
            'location_id': self.location_id,
            'location_name': self.location.name if self.location else '',
            'carrier_type': self.carrier_type,
            'sides': self.sides,
            'dimensions': self.dimensions,
            'technical_condition': self.technical_condition,
            'installation_date': self.installation_date.isoformat() if self.installation_date else None,
            'last_inspection_date': self.last_inspection_date.isoformat() if self.last_inspection_date else None,
            'status': self.status,
            'notes': self.notes
        }

    def active_advertisements(self):
        """Zwraca listę aktywnych reklam na tym nośniku."""
        today = datetime.utcnow().date()
        return self.advertisements.filter(
            Advertisement.start_date <= today,
            Advertisement.end_date >= today
        ).all()

    def has_active_advertisements(self):
        """Sprawdza, czy nośnik ma aktualnie aktywne reklamy."""
        return len(self.active_advertisements()) > 0

    def get_advertisement_for_side(self, side):
        """Zwraca aktywną reklamę dla konkretnej strony nośnika."""
        today = datetime.utcnow().date()
        return self.advertisements.filter(
            Advertisement.side == side,
            Advertisement.start_date <= today,
            Advertisement.end_date >= today
        ).first()