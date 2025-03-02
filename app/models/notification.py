from datetime import datetime
from app.extensions import db

class Notification(db.Model):
    """Model reprezentujący powiadomienie."""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'warning', 'info', 'success', 'danger'
    target_url = db.Column(db.String(255))  # URL do strony związanej z powiadomieniem
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.title}>'
    
    def to_dict(self):
        """Konwertuje powiadomienie do słownika."""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'type': self.type,
            'target_url': self.target_url,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def create_ad_expiry_notification(cls, ad):
        """Tworzy powiadomienie o zbliżającym się końcu kampanii reklamowej."""
        from app.extensions import db
        
        title = f"Kampania {ad.title or 'bez tytułu'} wkrótce się zakończy"
        message = f"Kampania reklamowa #{ad.id} ({ad.title or 'bez tytułu'}) zakończy się {ad.end_date.strftime('%d.%m.%Y')}."
        
        notification = cls(
            title=title,
            message=message,
            type='warning',
            target_url=f"/ads/{ad.id}"
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return notification
    
    @classmethod
    def create_carrier_inspection_notification(cls, carrier):
        """Tworzy powiadomienie o nośniku wymagającym inspekcji."""
        from app.extensions import db
        
        title = f"Nośnik #{carrier.id} wymaga inspekcji"
        message = f"Nośnik {carrier.carrier_type} w lokalizacji {carrier.location.name if carrier.location else 'brak'} wymaga inspekcji."
        
        notification = cls(
            title=title,
            message=message,
            type='info',
            target_url=f"/carriers/{carrier.id}"
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return notification
    
    @classmethod
    def get_unread_count(cls):
        """Zwraca liczbę nieprzeczytanych powiadomień."""
        return cls.query.filter_by(is_read=False).count()
    
    @classmethod
    def get_recent(cls, limit=5):
        """Zwraca listę najnowszych powiadomień."""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()