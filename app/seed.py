from app.models.location import Location
from app.models.ad_carrier import AdCarrier
from app.extensions import db
from datetime import datetime


def seed_initial_data():
    """Dodaje początkowe dane do bazy, jeśli jeszcze nie istnieją."""

    # Sprawdź, czy już mamy jakieś lokalizacje
    if Location.query.count() == 0:
        # Dodaj lokalizacje citylightów w Kraśniku
        citylight_locations = [
            {
                'name': 'Balladyny (Osiedle Młodych 02)',
                'coordinates': '50.941520, 22.221293',
                'address': 'ul. Balladyny, Osiedle Młodych, Kraśnik',
                'description': 'Citylight dwustronny na przystanku',
                'permanent': True
            },
            {
                'name': 'Budzyń 01',
                'coordinates': '50.936001, 22.214556',
                'address': 'ul. Budzyń 01, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Budzyń 02',
                'coordinates': '50.937001, 22.213556',
                'address': 'ul. Budzyń 02, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Cmentarz Komunalny 02',
                'coordinates': '50.957651, 22.223095',
                'address': 'Przy Cmentarzu Komunalnym, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Inwalidów 02',
                'coordinates': '50.945651, 22.221095',
                'address': 'ul. Inwalidów 02, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Jednostka Wojskowa 02',
                'coordinates': '50.942651, 22.218095',
                'address': 'Przy Jednostce Wojskowej, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Kaufland 01 (przy McDonald\'s)',
                'coordinates': '50.958651, 22.224095',
                'address': 'Przy Kauflandzie, obok McDonald\'s, Kraśnik',
                'description': 'Citylight dwustronny na przystanku',
                'permanent': True
            },
            {
                'name': 'Kaufland 02',
                'coordinates': '50.959651, 22.224095',
                'address': 'Przy Kauflandzie 02, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Kościół św. Józefa',
                'coordinates': '50.947651, 22.223095',
                'address': 'Przy Kościele św. Józefa, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Koszary 01',
                'coordinates': '50.943651, 22.217095',
                'address': 'Przy Koszarach 01, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Koszary 02',
                'coordinates': '50.944651, 22.216095',
                'address': 'Przy Koszarach 02, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Marzenie 01',
                'coordinates': '50.946651, 22.219095',
                'address': 'Osiedle Marzenie 01, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Młyńska',
                'coordinates': '50.950651, 22.225095',
                'address': 'ul. Młyńska, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Osiedle Młodych 01',
                'coordinates': '50.940520, 22.222293',
                'address': 'Osiedle Młodych 01, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Osiedle Słoneczne',
                'coordinates': '50.939520, 22.220293',
                'address': 'Osiedle Słoneczne, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Piaski 01',
                'coordinates': '50.938520, 22.219293',
                'address': 'Piaski 01, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Piaski 02',
                'coordinates': '50.937520, 22.218293',
                'address': 'Piaski 02, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Piaski II 01',
                'coordinates': '50.936520, 22.217293',
                'address': 'Piaski II 01, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Piaski II 02 (zalew)',
                'coordinates': '50.935520, 22.216293',
                'address': 'Piaski II 02, przy zalewie, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Piłsudskiego 01',
                'coordinates': '50.950651, 22.220095',
                'address': 'ul. Piłsudskiego 01, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Piłsudskiego 02',
                'coordinates': '50.951651, 22.221095',
                'address': 'ul. Piłsudskiego 02, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Przystanek Kraśnik 01',
                'coordinates': '50.956651, 22.222095',
                'address': 'Przystanek Kraśnik 01, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Przystanek Kraśnik 02',
                'coordinates': '50.955651, 22.221095',
                'address': 'Przystanek Kraśnik 02, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Przystanek Kraśnik 03',
                'coordinates': '50.954651, 22.220095',
                'address': 'Przystanek Kraśnik 03, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Przystanek Kraśnik 04',
                'coordinates': '50.953651, 22.219095',
                'address': 'Przystanek Kraśnik 04, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Przystanek Kraśnik 05',
                'coordinates': '50.952651, 22.218095',
                'address': 'Przystanek Kraśnik 05, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Przystanek Kraśnik 06',
                'coordinates': '50.952651, 22.217095',
                'address': 'Przystanek Kraśnik 06, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Racławicka',
                'coordinates': '50.948651, 22.215095',
                'address': 'ul. Racławicka, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'ROD Marzenie 02',
                'coordinates': '50.947651, 22.214095',
                'address': 'ROD Marzenie 02, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Starostwo Powiatowe 02',
                'coordinates': '50.949651, 22.216095',
                'address': 'Przy Starostwie Powiatowym, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Strażacka',
                'coordinates': '50.945651, 22.213095',
                'address': 'ul. Strażacka, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Szkoła 2',
                'coordinates': '50.944651, 22.212095',
                'address': 'Przy Szkole 2, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Targowisko Miejskie',
                'coordinates': '50.943651, 22.211095',
                'address': 'Przy Targowisku Miejskim, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Urząd Miasta 01',
                'coordinates': '50.942651, 22.210095',
                'address': 'Przy Urzędzie Miasta 01, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Urząd Miasta 02',
                'coordinates': '50.941651, 22.209095',
                'address': 'Przy Urzędzie Miasta 02, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            },
            {
                'name': 'Zakrzowiecka',
                'coordinates': '50.940651, 22.208095',
                'address': 'ul. Zakrzowiecka, Kraśnik',
                'description': 'Citylight na przystanku',
                'permanent': True
            }
        ]

        # Dodaj lokalizacje banerów w Kraśniku
        banner_locations = [
            {
                'name': 'CKiP',
                'coordinates': '50.950682, 22.234802',
                'address': 'Przy Centrum Kultury i Promocji, Kraśnik',
                'description': 'Baner 500x250 cm',
                'permanent': True
            },
            {
                'name': 'Media Expert',
                'coordinates': '50.953365, 22.224926',
                'address': 'Przy Media Expert, Kraśnik',
                'description': 'Baner 508x239 cm',
                'permanent': True
            },
            {
                'name': 'Mickiewicza i Słowackiego',
                'coordinates': '50.960573, 22.225313',
                'address': 'Skrzyżowanie ul. Mickiewicza i Słowackiego, Kraśnik',
                'description': 'Baner 500x250 cm',
                'permanent': True
            },
            {
                'name': 'Park przy USC',
                'coordinates': '50.949682, 22.232802',
                'address': 'Park przy Urzędzie Stanu Cywilnego, Kraśnik',
                'description': 'Baner 400x200 cm',
                'permanent': True
            },
            {
                'name': 'Plac Wolności',
                'coordinates': '50.946954, 22.221636',
                'address': 'Plac Wolności, Kraśnik',
                'description': 'Baner 300x200 cm',
                'permanent': True
            },
            {
                'name': 'Przystanek Kraśnik',
                'coordinates': '50.954682, 22.231802',
                'address': 'Przystanek Kraśnik, główny przystanek, Kraśnik',
                'description': 'Baner 500x250 cm',
                'permanent': True
            },
            {
                'name': 'Punkt 9',
                'coordinates': '50.957682, 22.233802',
                'address': 'Lokalizacja Punkt 9, Kraśnik',
                'description': 'Baner',
                'permanent': True
            },
            {
                'name': 'Punkt 10',
                'coordinates': '50.958682, 22.234802',
                'address': 'Lokalizacja Punkt 10, Kraśnik',
                'description': 'Baner',
                'permanent': True
            },
            {
                'name': 'Punkt 11',
                'coordinates': '50.959682, 22.235802',
                'address': 'Lokalizacja Punkt 11, Kraśnik',
                'description': 'Baner',
                'permanent': True
            },
            {
                'name': 'Skrzyżowanie Krasińskiego z Wyszyńskiego',
                'coordinates': '50.947682, 22.230802',
                'address': 'Skrzyżowanie ul. Krasińskiego z ul. Wyszyńskiego, Kraśnik',
                'description': 'Baner',
                'permanent': True
            },
            {
                'name': 'Zalew parking',
                'coordinates': '50.934001, 22.214556',
                'address': 'Parking przy zalewie, Kraśnik',
                'description': 'Baner 500x250 cm',
                'permanent': True
            }
        ]

        # Łączymy obie listy
        locations = citylight_locations + banner_locations

        for loc_data in locations:
            location = Location(**loc_data)
            db.session.add(location)

        # Najpierw zapisz lokalizacje, żeby mieć dostęp do ich ID
        db.session.commit()

        # Dodaj nośniki dla każdej lokalizacji
        carriers = []

        # Dodaj nośniki typu citylight
        for location in Location.query.filter(Location.description.like('%Citylight%')).all():
            # Określenie liczby stron (jednostronny lub dwustronny)
            sides = 2 if "dwustronny" in location.description.lower() else 1

            carriers.append({
                'location_id': location.id,
                'carrier_type': 'citylight',
                'sides': sides,  # 1 lub 2 strony
                'dimensions': '118x175 cm',  # Standardowy wymiar citylight
                'technical_condition': 'Dobry',
                'installation_date': datetime.strptime('2023-01-15', '%Y-%m-%d').date(),
                'status': 'active'
            })

        # Dodaj nośniki typu baner
        for location in Location.query.filter(Location.name.in_([loc['name'] for loc in banner_locations])).all():
            # Wyciągnij wymiary z opisu, jeśli istnieją
            dimensions = '300x200 cm'  # Domyślny wymiar
            if 'cm' in location.description:
                import re
                match = re.search(r'(\d+x\d+) cm', location.description)
                if match:
                    dimensions = match.group(1) + ' cm'

            carriers.append({
                'location_id': location.id,
                'carrier_type': 'baner',
                'sides': 1,  # Banery zazwyczaj mają 1 stronę
                'dimensions': dimensions,
                'technical_condition': 'Dobry',
                'installation_date': datetime.strptime('2023-02-10', '%Y-%m-%d').date(),
                'status': 'active'
            })

        # Dodaj nośniki do bazy
        for carrier_data in carriers:
            carrier = AdCarrier(**carrier_data)
            db.session.add(carrier)

        db.session.commit()
        print("Dodano początkowe dane do bazy")