from datetime import datetime
from app.extensions import db


class Photo(db.Model):
    """Model reprezentujący zdjęcie reklamy."""
    __tablename__ = 'photos'

    id = db.Column(db.Integer, primary_key=True)
    advertisement_id = db.Column(db.Integer, db.ForeignKey('advertisements.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    taken_at = db.Column(db.DateTime)
    gps_latitude = db.Column(db.Float)
    gps_longitude = db.Column(db.Float)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)

    # Relacje
    advertisement = db.relationship('Advertisement', back_populates='photos')

    def __repr__(self):
        return f'<Photo {self.id} for ad {self.advertisement_id}>'

    def to_dict(self):
        """Konwertuje model do słownika do użycia w API."""
        return {
            'id': self.id,
            'advertisement_id': self.advertisement_id,
            'filename': self.filename,
            'thumbnail_url': f'/static/uploads/thumbnails/{self.filename}',
            'original_url': f'/static/uploads/original/{self.filename}',
            'taken_at': self.taken_at.isoformat() if self.taken_at else None,
            'upload_date': self.upload_date.isoformat()
        }

    @property
    def thumbnail_url(self):
        """Zwraca URL do miniatury zdjęcia."""
        return f'/static/uploads/thumbnails/{self.filename}'

    @property
    def original_url(self):
        """Zwraca URL do oryginalnego zdjęcia."""
        return f'/static/uploads/original/{self.filename}'