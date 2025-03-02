from datetime import datetime
from app.extensions import db
import logging


class Location(db.Model):
    """Model reprezentujący lokalizację nośnika reklamowego."""
    __tablename__ = 'locations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    coordinates = db.Column(db.String(50), nullable=False)  # Format "lat,lon"
    address = db.Column(db.String(255))
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    permanent = db.Column(db.Boolean, default=True)  # Stała lokalizacja (zawsze widoczna)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacje
    carriers = db.relationship('AdCarrier', back_populates='location', lazy='dynamic')

    def __repr__(self):
        return f'<Location {self.name}>'

    def to_dict(self):
        """Konwertuje model do słownika do użycia w API."""
        return {
            'id': self.id,
            'name': self.name,
            'coordinates': self.coordinates,
            'address': self.address,
            'description': self.description,
            'active': self.active,
            'permanent': self.permanent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @property
    def lat(self):
        """Zwraca szerokość geograficzną."""
        if not self.coordinates:
            return None

        try:
            # Obsługa różnych formatów: "lat,lon", "lat, lon", "lat ,lon"
            coords = self.coordinates.replace(' ', '').split(',')
            if len(coords) >= 2:
                return float(coords[0])
            logging.warning(f"Nieprawidłowy format coordinates '{self.coordinates}' dla lokalizacji {self.id}")
            return None
        except (ValueError, IndexError) as e:
            logging.error(f"Błąd parsowania lat z '{self.coordinates}' dla lokalizacji {self.id}: {str(e)}")
            return None

    @property
    def lon(self):
        """Zwraca długość geograficzną."""
        if not self.coordinates:
            return None

        try:
            # Obsługa różnych formatów: "lat,lon", "lat, lon", "lat ,lon"
            coords = self.coordinates.replace(' ', '').split(',')
            if len(coords) >= 2:
                return float(coords[1])
            logging.warning(f"Nieprawidłowy format coordinates '{self.coordinates}' dla lokalizacji {self.id}")
            return None
        except (ValueError, IndexError) as e:
            logging.error(f"Błąd parsowania lon z '{self.coordinates}' dla lokalizacji {self.id}: {str(e)}")
            return None

    @property
    def active_carriers(self):
        """Zwraca aktywne nośniki w tej lokalizacji."""
        return self.carriers.filter_by(status='active').all()

    def has_active_advertisements(self):
        """Sprawdza, czy lokalizacja ma aktywne reklamy."""
        for carrier in self.active_carriers:
            if carrier.has_active_advertisements():
                return True
        return False