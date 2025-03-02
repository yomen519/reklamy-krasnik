from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

class LocationForm(FlaskForm):
    """Formularz do dodawania/edycji lokalizacji."""
    name = StringField('Nazwa', validators=[DataRequired(), Length(max=100)])
    coordinates = StringField('Współrzędne (lat,lon)', validators=[DataRequired(), Length(max=50)])
    address = StringField('Adres', validators=[Optional(), Length(max=255)])
    description = TextAreaField('Opis', validators=[Optional(), Length(max=1000)])
    active = BooleanField('Aktywna', default=True)
    permanent = BooleanField('Stała lokalizacja (zawsze widoczna)', default=True)
    submit = SubmitField('Zapisz')