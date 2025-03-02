from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from datetime import date

class AdForm(FlaskForm):
    """Formularz do dodawania/edycji reklam."""
    carrier_id = SelectField('Nośnik', coerce=int, validators=[DataRequired()])
    side = SelectField('Strona nośnika', coerce=int, validators=[DataRequired(),
        NumberRange(min=1, max=2, message='Strona musi mieć wartość 1 lub 2')])
    title = StringField('Tytuł kampanii', validators=[Optional(), Length(max=100)])
    client = StringField('Klient', validators=[Optional(), Length(max=100)])
    start_date = DateField('Data rozpoczęcia', format='%Y-%m-%d', validators=[DataRequired()], default=date.today)
    end_date = DateField('Data zakończenia', format='%Y-%m-%d', validators=[DataRequired()], default=date.today)
    status = SelectField('Status', choices=[
        ('scheduled', 'Zaplanowana'),
        ('active', 'Aktywna'),
        ('finished', 'Zakończona')
    ], validators=[DataRequired()])
    notes = TextAreaField('Uwagi', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Zapisz')

class PhotoUploadForm(FlaskForm):
    """Formularz do przesyłania zdjęć."""
    photos = FileField('Zdjęcia', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Tylko pliki JPG i PNG są dozwolone.')
    ])
    submit = SubmitField('Prześlij')