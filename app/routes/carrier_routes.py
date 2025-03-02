from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.ad_carrier import AdCarrier
from app.models.location import Location
from app.forms.carrier_forms import CarrierForm
from app.extensions import db
from datetime import datetime

carrier_bp = Blueprint('carrier', __name__)


@carrier_bp.route('/')
def index():
    """Lista nośników reklamowych."""
    # Pobieramy parametry filtrowania
    carrier_type = request.args.get('type')
    status = request.args.get('status')
    search = request.args.get('search')

    # Budujemy zapytanie
    query = AdCarrier.query

    # Stosujemy filtry
    if carrier_type:
        query = query.filter_by(carrier_type=carrier_type)
    if status:
        query = query.filter_by(status=status)
    if search:
        query = query.join(Location).filter(Location.name.ilike(f'%{search}%'))

    # Pobieramy wyniki
    carriers = query.order_by(AdCarrier.id).all()

    return render_template('carriers/index.html', carriers=carriers)


@carrier_bp.route('/add', methods=['GET', 'POST'])
def add():
    """Dodawanie nowego nośnika."""
    form = CarrierForm()

    # Pobieramy lokalizacje do wyboru
    form.location_id.choices = [(loc.id, loc.name) for loc in
                                Location.query.filter_by(active=True).order_by(Location.name).all()]

    if form.validate_on_submit():
        carrier = AdCarrier(
            location_id=form.location_id.data,
            carrier_type=form.carrier_type.data,
            sides=form.sides.data,
            dimensions=form.dimensions.data,
            technical_condition=form.technical_condition.data,
            installation_date=form.installation_date.data,
            status=form.status.data,
            notes=form.notes.data
        )
        db.session.add(carrier)
        db.session.commit()
        flash('Nośnik dodany pomyślnie!', 'success')
        return redirect(url_for('carrier.view', carrier_id=carrier.id))

    return render_template('carriers/add.html', form=form)


@carrier_bp.route('/<int:carrier_id>', methods=['GET'])
def view(carrier_id):
    """Szczegóły nośnika."""
    carrier = AdCarrier.query.get_or_404(carrier_id)
    return render_template('carriers/view.html', carrier=carrier)


@carrier_bp.route('/edit/<int:carrier_id>', methods=['GET', 'POST'])
def edit(carrier_id):
    """Edycja nośnika."""
    carrier = AdCarrier.query.get_or_404(carrier_id)
    form = CarrierForm(obj=carrier)

    # Pobieramy lokalizacje do wyboru
    form.location_id.choices = [(loc.id, loc.name) for loc in
                                Location.query.filter_by(active=True).order_by(Location.name).all()]

    if form.validate_on_submit():
        carrier.location_id = form.location_id.data
        carrier.carrier_type = form.carrier_type.data
        carrier.sides = form.sides.data
        carrier.dimensions = form.dimensions.data
        carrier.technical_condition = form.technical_condition.data
        carrier.installation_date = form.installation_date.data
        carrier.status = form.status.data
        carrier.notes = form.notes.data

        db.session.commit()
        flash('Nośnik zaktualizowany pomyślnie!', 'success')
        return redirect(url_for('carrier.view', carrier_id=carrier.id))

    return render_template('carriers/edit.html', form=form, carrier=carrier)


@carrier_bp.route('/delete/<int:carrier_id>', methods=['POST'])
def delete(carrier_id):
    """Usuwanie nośnika."""
    carrier = AdCarrier.query.get_or_404(carrier_id)

    # Sprawdzamy, czy nośnik ma aktywne reklamy
    if carrier.advertisements.count() > 0:
        flash('Nie można usunąć nośnika, który ma przypisane reklamy.', 'danger')
        return redirect(url_for('carrier.view', carrier_id=carrier.id))

    location_id = carrier.location_id
    db.session.delete(carrier)
    db.session.commit()

    flash('Nośnik usunięty pomyślnie!', 'success')
    return redirect(url_for('location.view', location_id=location_id))