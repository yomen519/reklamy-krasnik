from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models.advertisement import Advertisement
from app.models.ad_carrier import AdCarrier
from app.models.photo import Photo
from app.forms.ad_forms import AdForm, PhotoUploadForm
from app.extensions import db, csrf
from app.services.image_service import save_image
from datetime import datetime, timezone
import os

ad_bp = Blueprint('ad', __name__)


@ad_bp.route('/')
def index():
    """Lista reklam."""
    ads = Advertisement.query.order_by(Advertisement.id.desc()).all()
    return render_template('advertisements/index.html', ads=ads)


@ad_bp.route('/add', methods=['GET', 'POST'])
def add():
    """Dodawanie nowej reklamy."""
    carrier_id = request.args.get('carrier_id', type=int)
    form = AdForm()
    
    # Pobieramy listę nośników do wyboru
    form.carrier_id.choices = [(c.id, f"{c.carrier_type.capitalize()} #{c.id} - {c.location.name if c.location else 'Brak lokalizacji'}") 
                              for c in AdCarrier.query.all()]
    
    # Jeśli nie ma żadnych nośników, dodajemy pustą opcję
    if not form.carrier_id.choices:
        form.carrier_id.choices = [(0, 'Brak dostępnych nośników')]
    
    # Inicjalizacja opcji dla pola side (strona nośnika)
    if carrier_id:
        # Jeśli mamy określony carrier_id, ustawiamy wartość w formularzu
        form.carrier_id.data = carrier_id
        carrier = AdCarrier.query.get_or_404(carrier_id)
        # Ustawiamy dostępne strony na podstawie liczby stron nośnika
        form.side.choices = [(i, f"Strona {i}") for i in range(1, carrier.sides + 1)]
    else:
        # Domyślnie inicjalizujemy pole side z jedną opcją
        form.side.choices = [(1, "Strona 1")]
    
    if request.method == 'POST':
        # Aktualizujemy wybór stron na podstawie wybranego nośnika w formularzu
        selected_carrier_id = form.carrier_id.data
        if selected_carrier_id:
            selected_carrier = AdCarrier.query.get(selected_carrier_id)
            if selected_carrier:
                form.side.choices = [(i, f"Strona {i}") for i in range(1, selected_carrier.sides + 1)]
    
    if form.validate_on_submit():
        ad = Advertisement(
            carrier_id=form.carrier_id.data,
            side=form.side.data,
            title=form.title.data,
            client=form.client.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            status=form.status.data,
            notes=form.notes.data
        )
        db.session.add(ad)
        db.session.commit()
        flash('Reklama dodana pomyślnie!', 'success')
        return redirect(url_for('ad.view', ad_id=ad.id))
    
    return render_template('advertisements/add.html', form=form, carrier_id=carrier_id)


@ad_bp.route('/<int:ad_id>', methods=['GET'])
def view(ad_id):
    """Szczegóły reklamy."""
    ad = Advertisement.query.get_or_404(ad_id)
    return render_template('advertisements/view.html', ad=ad)


@ad_bp.route('/edit/<int:ad_id>', methods=['GET', 'POST'])
@ad_bp.route('/edit/<int:ad_id>', methods=['GET', 'POST'])
@csrf.exempt
def edit(ad_id):
    ad = Advertisement.query.get_or_404(ad_id)
    form = AdForm(obj=ad)

    # Pobieramy listę nośników do wyboru
    form.carrier_id.choices = [
        (c.id, f"{c.carrier_type.capitalize()} #{c.id} - {c.location.name if c.location else 'Brak lokalizacji'}")
        for c in AdCarrier.query.all()]

    # Ustawiamy dostępne strony na podstawie liczby stron nośnika
    carrier = AdCarrier.query.get(ad.carrier_id)
    if carrier:
        form.side.choices = [(i, f"Strona {i}") for i in range(1, carrier.sides + 1)]

    if form.validate_on_submit():
        ad.carrier_id = form.carrier_id.data
        ad.side = form.side.data
        ad.title = form.title.data
        ad.client = form.client.data
        ad.start_date = form.start_date.data
        ad.end_date = form.end_date.data
        ad.status = form.status.data
        ad.notes = form.notes.data

        db.session.commit()
        flash('Reklama zaktualizowana pomyślnie!', 'success')
        return redirect(url_for('ad.view', ad_id=ad.id))

    return render_template('advertisements/edit.html', form=form, ad=ad)


@ad_bp.route('/upload-photos/<int:ad_id>', methods=['GET', 'POST'])
@csrf.exempt
def upload_photos(ad_id):
    """Upload zdjęć dla reklamy."""
    ad = Advertisement.query.get_or_404(ad_id)
    form = PhotoUploadForm()

    if request.method == 'POST':
        # Obsługa upload za pomocą żądania POST - bez używania wtforms dla plików
        if 'photos' not in request.files:
            flash('Nie wybrano żadnych plików.', 'danger')
            return redirect(request.url)

        files = request.files.getlist('photos')

        if not files or files[0].filename == '':
            flash('Nie wybrano żadnych plików.', 'danger')
            return redirect(request.url)

        success_count = 0
        for file in files:
            image_data = save_image(file)
            if image_data:
                photo = Photo(
                    advertisement_id=ad.id,
                    filename=image_data['filename'],
                    original_filename=image_data['original_filename'],
                    taken_at=image_data.get('taken_at'),
                    gps_latitude=image_data.get('gps_latitude'),
                    gps_longitude=image_data.get('gps_longitude'),
                    upload_date=datetime.now(timezone.utc)
                )
                db.session.add(photo)
                success_count += 1

        if success_count > 0:
            db.session.commit()
            flash(f'Pomyślnie przesłano {success_count} zdjęć.', 'success')
            return redirect(url_for('ad.view', ad_id=ad.id))
        else:
            flash('Nie udało się przesłać żadnych zdjęć.', 'danger')

    return render_template('advertisements/upload_photos.html', form=form, ad=ad)


@ad_bp.route('/delete-photo/<int:photo_id>', methods=['POST', 'GET'])
@csrf.exempt
def delete_photo(photo_id):
    """Usuwanie zdjęcia."""
    from flask import current_app
    
    photo = Photo.query.get_or_404(photo_id)
    ad_id = photo.advertisement_id

    # Dodaj usuwanie plików (opcjonalnie, jeśli trzymasz pliki na dysku)
    original_path = os.path.join(current_app.config['ORIGINAL_FOLDER'], photo.filename)
    thumbnail_path = os.path.join(current_app.config['THUMBNAIL_FOLDER'], photo.filename)
    
    if os.path.exists(original_path):
        os.remove(original_path)
    if os.path.exists(thumbnail_path):
        os.remove(thumbnail_path)

    db.session.delete(photo)
    db.session.commit()

    flash('Zdjęcie zostało usunięte.', 'success')
    
    # Sprawdzamy, czy żądanie pochodzi z mapy
    if 'from_map' in request.args:
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        return redirect(url_for('main.index', lat=lat, lon=lon))
    
    return redirect(url_for('ad.view', ad_id=ad_id))


@ad_bp.route('/get-carrier-sides/<int:carrier_id>', methods=['GET'])
def get_carrier_sides(carrier_id):
    """API zwracające liczbę stron nośnika."""
    carrier = AdCarrier.query.get_or_404(carrier_id)
    sides = [(i, f"Strona {i}") for i in range(1, carrier.sides + 1)]
    
    # Jeśli nie ma stron, dodajmy domyślną opcję
    if not sides:
        sides = [(1, "Strona 1")]
        
    return jsonify(sides)


@ad_bp.route('/<int:ad_id>/photos/add', methods=['GET', 'POST'])
@csrf.exempt
def add_photos(ad_id):
    """Dodaje zdjęcia do reklamy z poziomu mapy."""
    ad = Advertisement.query.get_or_404(ad_id)
    
    if request.method == 'POST':
        if 'photos' not in request.files:
            flash('Nie wybrano plików', 'warning')
            return redirect(request.url)
        
        uploaded_files = request.files.getlist('photos')
        if not uploaded_files or uploaded_files[0].filename == '':
            flash('Nie wybrano plików', 'warning')
            return redirect(request.url)
        
        # Zapisujemy każde zdjęcie
        success_count = 0
        for file in uploaded_files:
            image_data = save_image(file)
            if image_data:
                # Tworzymy nowy obiekt Photo
                photo = Photo(
                    advertisement_id=ad.id,
                    filename=image_data['filename'],
                    original_filename=image_data['original_filename'],
                    taken_at=image_data.get('taken_at'),
                    gps_latitude=image_data.get('gps_latitude'),
                    gps_longitude=image_data.get('gps_longitude'),
                    upload_date=datetime.utcnow()
                )
                db.session.add(photo)
                success_count += 1
        
        if success_count > 0:
            db.session.commit()
            flash(f'Pomyślnie przesłano {success_count} zdjęć.', 'success')
        else:
            flash('Nie udało się przesłać żadnych zdjęć.', 'warning')
        
        # Sprawdzamy, czy żądanie pochodzi z mapy
        if 'from_map' in request.args:
            lat = request.args.get('lat')
            lon = request.args.get('lon')
            return redirect(url_for('main.index', lat=lat, lon=lon))
        
        return redirect(url_for('ad.index'))
    
    # Pobieramy listę aktywnych reklam do wyświetlenia jako podpowiedź
    today = datetime.utcnow().date()
    active_ads = Advertisement.query.filter(
        Advertisement.start_date <= today,
        Advertisement.end_date >= today
    ).order_by(Advertisement.end_date).all()
    
    return render_template('advertisements/add_photos.html', ad=ad)


@ad_bp.route('/batch-upload', methods=['GET', 'POST'])
@csrf.exempt
def batch_upload():
    """Masowe wczytywanie zdjęć z automatycznym przypisaniem."""
    from app.services.image_service import batch_process_images
    from app.models.advertisement import Advertisement
    from datetime import datetime
    from flask import session
    
    if request.method == 'POST':
        if 'photos' not in request.files:
            flash('Nie wybrano plików', 'warning')
            return redirect(request.url)
        
        files = request.files.getlist('photos')
        if not files or files[0].filename == '':
            flash('Nie wybrano plików', 'warning')
            return redirect(request.url)
        
        # Przetwarzamy zdjęcia
        results, unassigned_photos = batch_process_images(files, confidence_threshold=0.6)
        
        # Zapisujemy nieprzypisane zdjęcia w sesji, żeby użytkownik mógł je przypisać ręcznie
        if unassigned_photos:
            session['unassigned_photos'] = unassigned_photos
        
        # Wyświetlamy podsumowanie
        if results['auto_assigned'] > 0:
            flash(f'Automatycznie przypisano {results["auto_assigned"]} z {results["total"]} zdjęć.', 'success')
        
        if results['unassigned'] > 0:
            flash(f'{results["unassigned"]} zdjęć wymaga ręcznego przypisania.', 'warning')
            return redirect(url_for('ad.assign_batch'))
        
        if results['errors'] > 0:
            flash(f'Wystąpiły błędy podczas przetwarzania {results["errors"]} zdjęć.', 'danger')
        
        return redirect(url_for('ad.index'))
    
    # Pobieramy listę aktywnych reklam do wyświetlenia jako podpowiedź
    today = datetime.now(timezone.utc).date()
    active_ads = Advertisement.query.filter(
        Advertisement.start_date <= today,
        Advertisement.end_date >= today
    ).order_by(Advertisement.end_date).all()
    
    return render_template('advertisements/batch_upload.html', active_ads=active_ads)


@ad_bp.route('/assign-batch', methods=['GET', 'POST'])
@csrf.exempt
def assign_batch():
    """Ręczne przypisywanie nieprzypisanych zdjęć z masowego uploadu."""
    from app.models.photo import Photo
    from app.models.advertisement import Advertisement
    from flask import session
    
    unassigned_photos = session.get('unassigned_photos', [])
    
    if not unassigned_photos:
        flash('Nie ma zdjęć do przypisania', 'info')
        return redirect(url_for('ad.index'))
    
    if request.method == 'POST':
        # Pobieramy przypisania z formularza
        assignments = request.form.getlist('assignments')
        
        # Zapisujemy przypisania
        assigned_count = 0
        for i, ad_id in enumerate(assignments):
            if ad_id and ad_id.isdigit() and int(ad_id) > 0:
                ad_id = int(ad_id)
                photo_data = unassigned_photos[i]
                
                photo = Photo(
                    advertisement_id=ad_id,
                    filename=photo_data['filename'],
                    original_filename=photo_data['original_filename'],
                    taken_at=photo_data.get('taken_at'),
                    gps_latitude=photo_data.get('gps_latitude'),
                    gps_longitude=photo_data.get('gps_longitude'),
                    upload_date=datetime.utcnow()
                )
                db.session.add(photo)
                assigned_count += 1
        
        if assigned_count > 0:
            db.session.commit()
            flash(f'Przypisano {assigned_count} zdjęć', 'success')
            
        # Czyścimy sesję
        session.pop('unassigned_photos', None)
        
        return redirect(url_for('ad.index'))
    
    # Pobieramy listę wszystkich reklam do wyboru
    ads = Advertisement.query.all()  # Upewnij się, że pobierasz wszystkie reklamy
    
    return render_template('advertisements/assign_batch.html', 
                          unassigned_photos=unassigned_photos, 
                          ads=ads)