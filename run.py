from app import create_app, db
from app.models.location import Location
from app.models.ad_carrier import AdCarrier
from app.models.advertisement import Advertisement
from app.models.photo import Photo
from app.seed import seed_initial_data

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'Location': Location,
        'AdCarrier': AdCarrier,
        'Advertisement': Advertisement,
        'Photo': Photo
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Tworzy tabele w bazie danych
        seed_initial_data()  # Dodaje początkowe dane

    app.run(debug=True)