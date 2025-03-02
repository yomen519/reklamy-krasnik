from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.location import Location
from app.forms.location_forms import LocationForm
from app.extensions import db
from app.services.geo_service import geocode_address

location_bp = Blueprint('location', __name__)


@location_bp.route('/')
def index():
    """Lista lokalizacji."""
    locations = Location.query.order_by(Location.name).all()
    return render_template('locations/index.html', locations=locations)


@location_bp.route('/add', methods=['GET', 'POST'])
def add():
    """Dodawanie nowej lokalizacji."""
    form = LocationForm()
    if form.validate_on_submit():
        # Jeśli koordynaty są puste, próbujemy je uzyskać z adresu
        if not form.coordinates.data and form.address.data:
            coords = geocode_address(form.address.data)
            if coords:
                form.coordinates.data = coords
            else:
                flash('Nie udało się uzyskać współrzędnych dla podanego adresu', 'warning')

        location = Location(
            name=form.name.data,
            coordinates=form.coordinates.data,
            address=form.address.data,
            description=form.description.data,
            active=form.active.data,
            permanent=form.permanent.data
        )
        db.session.add(location)
        db.session.commit()
        flash('Lokalizacja dodana pomyślnie!', 'success')
        return redirect(url_for('location.index'))

    return render_template('locations/add.html', form=form)


@location_bp.route('/edit/<int:location_id>', methods=['GET', 'POST'])
def edit(location_id):
    """Edycja istniejącej lokalizacji."""
    location = Location.query.get_or_404(location_id)
    form = LocationForm(obj=location)

    if form.validate_on_submit():
        # Aktualizuj dane lokalizacji
        location.name = form.name.data
        location.coordinates = form.coordinates.data
        location.address = form.address.data
        location.description = form.description.data
        location.active = form.active.data
        location.permanent = form.permanent.data

        db.session.commit()
        flash('Lokalizacja zaktualizowana pomyślnie!', 'success')
        return redirect(url_for('location.index'))

    return render_template('locations/edit.html', form=form, location=location)


@location_bp.route('/delete/<int:location_id>', methods=['POST'])
def delete(location_id):
    """Usuwanie lokalizacji."""
    location = Location.query.get_or_404(location_id)

    # Sprawdź, czy lokalizacja ma powiązane nośniki
    if location.carriers.count() > 0:
        flash('Nie można usunąć lokalizacji, która ma powiązane nośniki reklamowe.', 'danger')
        return redirect(url_for('location.index'))

    db.session.delete(location)
    db.session.commit()
    flash('Lokalizacja usunięta pomyślnie!', 'success')
    return redirect(url_for('location.index'))