import os
import sys
import csv
from io import StringIO
from datetime import datetime

# Dodajemy ścieżkę katalogu głównego projektu do ścieżek systemowych
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app import create_app, db
from app.models.location import Location
from app.models.ad_carrier import AdCarrier


def fix_locations_from_csv():
    """Importuje i naprawia lokalizacje z danych CSV."""
    app = create_app()
    with app.app_context():
        # Sprawdzenie istniejących lokalizacji
        all_locations = Location.query.all()
        print(f"Znaleziono {len(all_locations)} lokalizacji w bazie danych.")

        # Sprawdzanie i naprawianie współrzędnych
        for location in all_locations:
            if location.lat is None or location.lon is None:
                print(
                    f"Lokalizacja {location.id}: {location.name} ma nieprawidłowe współrzędne: {location.coordinates}")

        # Czy chcemy wyczyścić istniejące lokalizacje?
        choice = input("Czy chcesz usunąć istniejące lokalizacje? (tak/nie): ")
        if choice.lower() in ['tak', 't', 'yes', 'y']:
            # Usuwamy wszystkie nośniki
            AdCarrier.query.delete()
            # Usuwamy wszystkie lokalizacje
            Location.query.delete()
            db.session.commit()
            print("Wszystkie lokalizacje i nośniki zostały usunięte.")

        # Importujemy dane banerów
        banners_csv_data = """WKT,nazwa,opis,data
POINT (22.185856 50.9444088),zalew parking 500x250,,
POINT (22.1561483 50.9632706),CKiP 500x250,,
POINT (22.2199046 50.9214142),Plac wolności 300x200,,
POINT (22.2288624 50.9219317),Przystanek Kraśnik 500x250,,
POINT (22.1562074 50.9603779),skrz.Krasińskiego z Wyszyńskiego,,
POINT (22.2215662 50.9294569),park przy USC 400x200,,
POINT (22.1725418 50.9629749),Media expert 508x239,,
POINT (22.1625549 50.9607366),Mickiewicza i Słowackiego 500x250,,
POINT (22.216691 50.9334572),Punkt 9,,
POINT (22.1846686 50.9565893),Punkt 10,,
POINT (22.1958337 50.9488272),Punkt 11,,"""

        # Importujemy dane citylightów
        citylights_csv_data = """WKT,nazwa,opis,stan tchniczny
POINT (22.1792849 50.962017),Kaufland 01przy MacDonald,2 str,nowy 
POINT (22.1858488 50.9575321),ROD Marzenie 02,2 str,nowy 
POINT (22.1861385 50.9564576),marzenie 01,2 str,nowy
POINT (22.2166736 50.9200435),Piłsudskiego 01,2 str,stary stan dobry
POINT (22.2164081 50.9200442),Piłsudskiego 02,2 stonny,stary stan dobry
POINT (22.221497 50.9198444),strażacka,2 str ,bardzo zły, rozbita szyba , problem z otwieraniem zniszczony środek
POINT (22.2531749 50.9290852),zakrzowiecka,2 str,stary stan dobry 
POINT (22.2327416 50.9267803),urząd miasta 01,1 str,stary stan dobry 
POINT (22.2318618 50.9264456),urząd miasta 02,2 str,stary
POINT (22.2279411 50.9254938),szkoła 2 ,2 str,stary stan dobry brak tabliczki z nazwą
POINT (22.1763375 50.9645994),inwalidów 02,2 str ,nowy 
POINT (22.1727822 50.9627733),osiedle młodych 02 Balladyny ME,2 str,nowy
POINT (22.1531705 50.9628409),Racławicka,2 str,stary zniszczone wnętrze problem z zamykaniem
POINT (22.1541129 50.9602615),Kościół św. Józefa,2 str,stary rozbita szyba od strony parkingu, wgnieciony przez samochód, często zastawiony parkującymi samochodami
POINT (22.1762467 50.9625909),kaufland 02,2 str,nowy
POINT (22.1941392 50.9504179),budzyń 01,1 str,stary stan bardzo zły, problem z zamykaniem, zniszczony środek
POINT (22.2760962 50.9315434),jednoska wojskowa 02,2 str,stary  zaniedbany pomazany grafiiti zniszczony środek 
POINT (22.2273556 50.9218851),Przystanek Kraśnik 01,2 str,nowy problem z otwieraniem 
POINT (22.2278652 50.9219358),Przystanek Kraśnik 02,2 str,nowy problem z otwieraniem
POINT (22.2285412 50.9220626),Przystanek Kraśnik 03,2 str,nowy problem z otwieraniem
POINT (22.22742 50.9217363),Przystanek Kraśnik 04,2 str,nowy problem z otwieraniem
POINT (22.2279859 50.9218039),Przystanek Kraśnik 05,2 str,nowy problem z otwieraniem
POINT (22.2287209 50.9218766),Przystanek Kraśnik 06,2 str,nowy problem z otwieraniem
POINT (22.1383382 50.9568994),cmentarz komunalny 02,2 str ,stary stan dobry
POINT (22.1634886 50.9633253),Starostwo powiatowe 02,1 stronny,stary
POINT (22.1702371 50.9633185),osiedle młodych01,2 str,stary ,zniszczony środek popękany plastik, problem z otwieraniem i zamykaniem
POINT (22.1777331 50.9640483),targowisko miejskie,2 str,rozbita szyba , ciężko się otwiera 
POINT (22.1939097 50.9510409),budzyń 02,2 str,stary stan dobry
POINT (22.1593064 50.9603823),osiedle słoneczne,2 stronny ,stary, zniszczony środek problem z zamykaniem
POINT (22.2217401 50.9288125),koszary 01,2 str  ,stary stan dobry
POINT (22.2220083 50.9292182),koszary 02,,
POINT (22.2127064 50.9365207),piaski 02,2 str.  ,stary stan dobry
POINT (22.2127707 50.9358108),piaski 01,1 str ,stary problem z otwieraniem
POINT (22.2043593 50.9422471),piaski II 01 ,,
POINT (22.2046597 50.9429366),Piaski II 02 zalew,,
POINT (22.2095361 50.9192445),Młyńska,,"""

        # Funkcja do parsowania liczby stron z opisu
        def parse_sides(description):
            if not description:
                return 1  # Domyślnie 1 strona

            description = description.lower()
            if '2 str' in description or '2 stron' in description:
                return 2
            elif '1 str' in description or '1 stron' in description:
                return 1
            return 1  # Domyślnie 1 strona

        # Dodajemy citylighty
        citylights_reader = csv.reader(StringIO(citylights_csv_data), delimiter=',')
        next(citylights_reader)  # Pomijanie wiersza nagłówkowego

        citylight_count = 0
        for row in citylights_reader:
            if len(row) >= 3:
                try:
                    # Parsowanie danych WKT
                    wkt = row[0]
                    name = row[1].strip()
                    description = row[2].strip() if len(row) > 2 else ""
                    tech_condition = row[3].strip() if len(row) > 3 else "Nie określono"

                    # Wyciąganie współrzędnych z formatu WKT: POINT (lon lat)
                    coords_str = wkt.replace('POINT (', '').replace(')', '')
                    lon, lat = coords_str.split()
                    coordinates = f"{lat},{lon}"  # Format lat,lon

                    # Określenie liczby stron
                    sides = parse_sides(description)

                    # Sprawdzenie, czy lokalizacja już istnieje
                    existing_location = Location.query.filter_by(name=name).first()
                    if existing_location:
                        print(f"Aktualizuję lokalizację citylight: {name}")
                        existing_location.coordinates = coordinates
                        existing_location.description = f"Citylight {sides}-stronny"
                        location = existing_location
                    else:
                        print(f"Dodaję nową lokalizację citylight: {name}")
                        location = Location(
                            name=name,
                            coordinates=coordinates,
                            address=name,
                            description=f"Citylight {sides}-stronny",
                            permanent=True,
                            active=True
                        )
                        db.session.add(location)

                    db.session.commit()  # Zapisujemy, aby mieć ID lokalizacji

                    # Sprawdzenie, czy nośnik już istnieje
                    carrier = AdCarrier.query.filter_by(location_id=location.id).first()
                    if not carrier:
                        carrier = AdCarrier(
                            location_id=location.id,
                            carrier_type='citylight',
                            sides=sides,
                            dimensions='118x175 cm',
                            technical_condition=tech_condition,
                            installation_date=datetime.now().date(),
                            status='active'
                        )
                        db.session.add(carrier)
                        citylight_count += 1
                    else:
                        carrier.sides = sides
                        carrier.technical_condition = tech_condition
                except Exception as e:
                    print(f"Błąd przy przetwarzaniu citylighta {row}: {e}")
                    continue

        # Parsowanie danych banerów
        banners_reader = csv.reader(StringIO(banners_csv_data), delimiter=',')
        next(banners_reader)  # Pomijanie wiersza nagłówkowego

        banner_count = 0
        for row in banners_reader:
            if len(row) >= 3:
                # Parsowanie danych WKT
                wkt = row[0]
                try:
                    # Wyciąganie współrzędnych z formatu WKT: POINT (lon lat)
                    coords_str = wkt.replace('POINT (', '').replace(')', '')
                    lon, lat = coords_str.split()
                    coordinates = f"{lat},{lon}"  # Format lat,lon

                    name = row[1].strip()
                    description = row[2].strip() if len(row) > 2 else ""

                    # Określenie wymiarów, jeśli są podane w nazwie
                    dimensions = ""
                    if "x" in name and any(c.isdigit() for c in name):
                        parts = name.split()
                        for part in parts:
                            if "x" in part and any(c.isdigit() for c in part):
                                dimensions = part + " cm"
                                break

                    # Sprawdzenie, czy lokalizacja już istnieje
                    existing_location = Location.query.filter_by(name=name).first()
                    if existing_location:
                        print(f"Aktualizuję lokalizację baner: {name}")
                        existing_location.coordinates = coordinates
                        location = existing_location
                    else:
                        print(f"Dodaję nową lokalizację baner: {name}")
                        location = Location(
                            name=name,
                            coordinates=coordinates,
                            address=name,
                            description=description or "Baner reklamowy",
                            permanent=True,
                            active=True
                        )
                        db.session.add(location)

                    db.session.commit()  # Zapisujemy, aby mieć ID lokalizacji

                    # Sprawdzenie, czy nośnik już istnieje
                    carrier = AdCarrier.query.filter_by(location_id=location.id).first()
                    if not carrier:
                        carrier = AdCarrier(
                            location_id=location.id,
                            carrier_type='baner',
                            sides=1,
                            dimensions=dimensions if dimensions else '300x200 cm',
                            technical_condition='Dobry',
                            status='active'
                        )
                        db.session.add(carrier)
                        banner_count += 1
                    else:
                        if dimensions and not carrier.dimensions:
                            carrier.dimensions = dimensions
                except Exception as e:
                    print(f"Błąd przy przetwarzaniu banera {row}: {e}")
                    continue

        db.session.commit()
        print(f"Zaimportowano {citylight_count} lokalizacji citylightów i {banner_count} lokalizacji banerów.")

        # Sprawdzanie poprawności danych po imporcie
        all_locations_after = Location.query.all()
        invalid_count = 0
        for location in all_locations_after:
            if location.lat is None or location.lon is None:
                print(
                    f"UWAGA: Lokalizacja {location.id}: {location.name} nadal ma nieprawidłowe współrzędne: {location.coordinates}")
                invalid_count += 1

        if invalid_count == 0:
            print("Wszystkie lokalizacje mają poprawne współrzędne.")
        else:
            print(f"{invalid_count} lokalizacji wciąż ma nieprawidłowe współrzędne.")


if __name__ == "__main__":
    fix_locations_from_csv()