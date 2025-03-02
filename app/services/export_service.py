import csv
import io
import os
from datetime import datetime
from flask import current_app
import xlsxwriter
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def generate_csv(data, headers):
    """
    Generuje plik CSV z danych.
    
    Args:
        data: Lista list danych
        headers: Lista nagłówków kolumn
        
    Returns:
        BytesIO: Bufor zawierający plik CSV
    """
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Zapisz nagłówki
    writer.writerow(headers)
    
    # Zapisz dane
    for row in data:
        writer.writerow(row)
    
    return output.getvalue()

def generate_excel(data, headers, sheet_name='Raport'):
    """
    Generuje plik Excel z danych.
    
    Args:
        data: Lista list danych
        headers: Lista nagłówków kolumn
        sheet_name: Nazwa arkusza
        
    Returns:
        BytesIO: Bufor zawierający plik Excel
    """
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet(sheet_name)
    
    # Styl nagłówka - uproszczony, bez problematycznego koloru
    header_format = workbook.add_format({
        'bold': True,
        'border': 1
    })
    
    # Dodajemy kolor bezpośrednio - metoda która działa w starszych wersjach
    header_format.set_bg_color('#3388ff')  # Tło
    header_format.set_font_color('white')  # Kolor tekstu
    header_format.set_align('center')
    header_format.set_valign('vcenter')
    
    # Styl danych
    data_format = workbook.add_format({
        'border': 1,
        'valign': 'vcenter'
    })
    
    # Zapisz nagłówki
    for col, header in enumerate(headers):
        worksheet.write(0, col, header, header_format)
    
    # Zapisz dane
    for row_idx, row in enumerate(data):
        for col_idx, cell in enumerate(row):
            worksheet.write(row_idx + 1, col_idx, cell, data_format)
    
    # Dostosuj szerokość kolumn
    for i, header in enumerate(headers):
        worksheet.set_column(i, i, len(str(header)) + 5)
    
    workbook.close()
    output.seek(0)
    
    return output

def generate_pdf(data, headers, title, orientation='portrait'):
    """
    Generuje plik PDF z danych.
    
    Args:
        data: Lista list danych
        headers: Lista nagłówków kolumn
        title: Tytuł raportu
        orientation: Orientacja strony ('portrait' lub 'landscape')
        
    Returns:
        BytesIO: Bufor zawierający plik PDF
    """
    from reportlab.lib.enums import TA_CENTER
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # Próba rejestracji uniwersalnego fonta
    try:
        # Standardowa ścieżka do systemowych fontów Windows
        pdfmetrics.registerFont(TTFont('Arial', 'C:\\Windows\\Fonts\\arial.ttf'))
        pdfmetrics.registerFont(TTFont('ArialBold', 'C:\\Windows\\Fonts\\arialbd.ttf'))
        font_name = 'Arial'
        font_name_bold = 'ArialBold'
        print("Zarejestrowano font Arial")
    except:
        # Jeśli nie udało się, używamy domyślnego Helvetica
        font_name = 'Helvetica'
        font_name_bold = 'Helvetica-Bold'
        print("Nie udało się załadować fonta Arial, używam Helvetica")
    
    output = io.BytesIO()
    
    # Ustawienia strony
    if orientation == 'landscape':
        pagesize = landscape(A4)
    else:
        pagesize = A4
    
    # Tworzenie dokumentu
    doc = SimpleDocTemplate(
        output,
        pagesize=pagesize,
        title=title,
        author="System Reklam Kraśnik"
    )
    
    # Przygotowanie elementów dokumentu
    elements = []
    
    # Style
    styles = getSampleStyleSheet()
    
    # Definiowanie własnego stylu dla tytułu
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name_bold,
        alignment=TA_CENTER
    )
    
    # Dodanie tytułu (UTF-8 enkodowane)
    elements.append(Paragraph(title, title_style))
    elements.append(Spacer(1, 20))
    
    # Konwersja danych do unicode
    unicode_data = []
    for row in data:
        unicode_row = []
        for cell in row:
            if isinstance(cell, str):
                unicode_row.append(cell)
            else:
                unicode_row.append(str(cell))
        unicode_data.append(unicode_row)
    
    # Przygotowanie tabeli
    table_data = [headers] + unicode_data
    
    # Tworzenie tabeli
    table = Table(table_data)
    
    # Styl tabeli
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), font_name_bold),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
    ])
    table.setStyle(table_style)
    
    # Dodanie tabeli do dokumentu
    elements.append(table)
    
    # Generowanie PDF
    doc.build(elements)
    
    output.seek(0)
    return output

def get_available_carriers_report(start_date=None, end_date=None, carrier_type=None):
    """
    Generuje raport dostępnych nośników reklamowych w wybranym okresie.
    
    Args:
        start_date: Data początkowa (opcjonalnie)
        end_date: Data końcowa (opcjonalnie)
        carrier_type: Typ nośnika (opcjonalnie)
        
    Returns:
        tuple: (data, headers) dla raportu
    """
    from app.models.location import Location
    from app.models.ad_carrier import AdCarrier
    from app.models.advertisement import Advertisement
    from sqlalchemy import and_, not_
    
    # Przygotowanie zapytania o nośniki
    query = AdCarrier.query.filter_by(status='active')
    
    # Filtrowanie po typie
    if carrier_type:
        query = query.filter_by(carrier_type=carrier_type)
    
    carriers = query.all()
    
    # Przygotowanie danych raportu
    headers = ['ID', 'Typ', 'Lokalizacja', 'Wymiary', 'Strony', 'Status', 'Dostępność']
    data = []
    
    for carrier in carriers:
        # Sprawdzenie dostępności każdej strony nośnika
        for side in range(1, carrier.sides + 1):
            # Sprawdzamy, czy na tej stronie jest reklama w wybranym okresie
            side_busy = False
            
            # Jeśli podano okres, sprawdzamy czy strona jest zajęta w tym okresie
            if start_date and end_date:
                ads = Advertisement.query.filter(
                    Advertisement.carrier_id == carrier.id,
                    Advertisement.side == side,
                    not_(and_(
                        Advertisement.end_date < start_date,
                        Advertisement.start_date > end_date
                    ))
                ).all()
                
                side_busy = len(ads) > 0
            
            # Status dostępności
            if side_busy:
                availability = "Zajęty"
            else:
                availability = "Dostępny"
            
            # Dodanie danych do raportu
            data.append([
                carrier.id,
                'Citylight' if carrier.carrier_type == 'citylight' else 'Baner',
                carrier.location.name if carrier.location else 'Brak lokalizacji',
                carrier.dimensions or 'Nie określono',
                f"Strona {side}/{carrier.sides}",
                carrier.status,
                availability
            ])
    
    return data, headers

def get_ad_campaigns_report(start_date=None, end_date=None, client=None):
    """
    Generuje raport kampanii reklamowych w wybranym okresie.
    
    Args:
        start_date: Data początkowa (opcjonalnie)
        end_date: Data końcowa (opcjonalnie)
        client: Nazwa klienta (opcjonalnie)
        
    Returns:
        tuple: (data, headers) dla raportu
    """
    from app.models.advertisement import Advertisement
    
    # Przygotowanie zapytania
    query = Advertisement.query
    
    # Filtrowanie po datach
    if start_date:
        query = query.filter(Advertisement.end_date >= start_date)
    if end_date:
        query = query.filter(Advertisement.start_date <= end_date)
    
    # Filtrowanie po kliencie
    if client:
        query = query.filter(Advertisement.client.ilike(f'%{client}%'))
    
    # Sortowanie
    ads = query.order_by(Advertisement.start_date.desc()).all()
    
    # Przygotowanie danych raportu
    headers = ['ID', 'Tytuł', 'Klient', 'Nośnik', 'Lokalizacja', 'Okres', 'Status', 'Zdjęć']
    data = []
    
    for ad in ads:
        # Formatowanie okresu
        try:
            if ad.start_date and ad.end_date:
                period = f"{ad.start_date.strftime('%d.%m.%Y')} - {ad.end_date.strftime('%d.%m.%Y')}"
            else:
                period = "Nie określono"
        except Exception:
            period = "Nie określono"
        
        # Bezpieczne uzyskanie typu nośnika
        carrier_type = "Brak"
        if ad.carrier and hasattr(ad.carrier, 'carrier_type') and ad.carrier.carrier_type:
            carrier_type = ad.carrier.carrier_type.capitalize()
        
        # Bezpieczne uzyskanie lokalizacji
        location = "Brak lokalizacji"
        if ad.carrier and hasattr(ad.carrier, 'location') and ad.carrier.location:
            location = ad.carrier.location.name
        
        # Bezpieczne uzyskanie statusu
        status = ad.status
        if hasattr(ad, 'status_pl'):
            status = ad.status_pl
        
        # Dodanie danych do raportu
        data.append([
            ad.id,
            ad.title or 'Bez tytułu',
            ad.client or 'Nie określono',
            f"{carrier_type} (strona {ad.side})",
            location,
            period,
            status,
            len(ad.photos) if hasattr(ad, 'photos') else 0
        ])
    
    return data, headers