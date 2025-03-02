from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class CarrierForm(FlaskForm):
    """Formularz do dodawania/edycji nośnika reklamowego."""
    location_id = SelectField('Lokalizacja', coerce=int, validators=[DataRequired()])
    carrier_type = SelectField('Typ nośnika', choices=[
        ('citylight', 'Citylight'),
        ('baner', 'Baner')
    ], validators=[DataRequired()])
    sides = IntegerField('Liczba stron', default=1, validators=[
        DataRequired(),
        NumberRange(min=1, max=2, message='Nośnik może mieć 1 lub 2 strony')
    ])
    dimensions = StringField('Wymiary (np. 118x175 cm)', validators=[Optional(), Length(max=50)])
    technical_condition = TextAreaField('Stan techniczny', validators=[Optional(), Length(max=1000)])
    installation_date = DateField('Data instalacji', format='%Y-%m-%d', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('active', 'Aktywny'),
        ('damaged', 'Uszkodzony'),
        ('repair_needed', 'Wymaga naprawy'),
        ('inactive', 'Nieaktywny')
    ], validators=[DataRequired()])
    notes = TextAreaField('Uwagi', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Zapisz')