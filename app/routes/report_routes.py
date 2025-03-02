from flask import Blueprint, render_template, request, send_file, make_response, redirect, url_for, flash
from datetime import datetime
from io import BytesIO
from app.services.export_service import (
    generate_csv, generate_excel, generate_pdf,
    get_available_carriers_report, get_ad_campaigns_report
)

report_bp = Blueprint('report', __name__)

@report_bp.route('/')
def index():
    """Strona główna z listą dostępnych raportów."""
    return render_template('reports/index.html')

@report_bp.route('/available-carriers', methods=['GET', 'POST'])
def available_carriers():
    """Raport dostępnych nośników reklamowych."""
    from app.models.ad_carrier import AdCarrier
    
    # Przygotowanie formularza filtrowania
    carrier_types = [('', 'Wszystkie'), ('citylight', 'Citylighty'), ('baner', 'Banery')]
    
    # Obsługa filtrowania i eksportu
    if request.method == 'POST':
        # Pobieranie parametrów
        start_date = request.form.get('start_date')
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            
        end_date = request.form.get('end_date')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
        carrier_type = request.form.get('carrier_type')
        export_format = request.form.get('export_format')
        
        # Generowanie danych raportu
        data, headers = get_available_carriers_report(start_date, end_date, carrier_type)
        
        # Eksport danych
        if export_format == 'csv':
            csv_data = generate_csv(data, headers)
            response = make_response(csv_data)
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = 'attachment; filename=dostepne_nosniki.csv'
            return response
            
        elif export_format == 'excel':
            excel_data = generate_excel(data, headers, 'Dostępne nośniki')
            return send_file(
                excel_data,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='dostepne_nosniki.xlsx'
            )
            
        elif export_format == 'pdf':
            pdf_data = generate_pdf(
                data, 
                headers, 
                f'Raport dostępnych nośników reklamowych',
                orientation='landscape'
            )
            return send_file(
                BytesIO(pdf_data.read()),
                mimetype='application/pdf',
                as_attachment=True,
                download_name='dostepne_nosniki.pdf'
            )
    
    # Domyślne wartości filtrów
    filters = {
        'start_date': request.form.get('start_date', datetime.now().strftime('%Y-%m-%d')),
        'end_date': request.form.get('end_date', ''),
        'carrier_type': request.form.get('carrier_type', '')
    }
    
    # Generowanie danych raportu dla widoku
    data, headers = get_available_carriers_report(
        datetime.strptime(filters['start_date'], '%Y-%m-%d').date() if filters['start_date'] else None,
        datetime.strptime(filters['end_date'], '%Y-%m-%d').date() if filters['end_date'] else None,
        filters['carrier_type']
    )
    
    return render_template('reports/available_carriers.html', 
                          data=data, 
                          headers=headers, 
                          filters=filters,
                          carrier_types=carrier_types)

@report_bp.route('/ad-campaigns', methods=['GET', 'POST'])
def ad_campaigns():
    """Raport kampanii reklamowych."""
    from app.models.advertisement import Advertisement
    
    # Przygotowanie listy klientów
    clients = [(ad.client, ad.client) for ad in Advertisement.query.filter(Advertisement.client != None).distinct(Advertisement.client)]
    clients = [('', 'Wszyscy')] + [(c[0], c[0]) for c in clients if c[0]]
    
    # Domyślne wartości filtrów
    filters = {
        'start_date': request.form.get('start_date', ''),
        'end_date': request.form.get('end_date', ''),
        'client': request.form.get('client', '')
    }
    
    # Obsługa filtrowania i eksportu
    if request.method == 'POST':
        try:
            # Pobieranie parametrów
            start_date = request.form.get('start_date')
            if start_date and start_date.strip():
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            else:
                start_date = None
                
            end_date = request.form.get('end_date')
            if end_date and end_date.strip():
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                end_date = None
                
            client = request.form.get('client')
            export_format = request.form.get('export_format')
            
            # Generowanie danych raportu
            data, headers = get_ad_campaigns_report(start_date, end_date, client)
            
            # Eksport danych
            if export_format == 'csv':
                csv_data = generate_csv(data, headers)
                response = make_response(csv_data)
                response.headers['Content-Type'] = 'text/csv; charset=utf-8'
                response.headers['Content-Disposition'] = 'attachment; filename=kampanie_reklamowe.csv'
                return response
                
            elif export_format == 'excel':
                excel_data = generate_excel(data, headers, 'Kampanie reklamowe')
                return send_file(
                    excel_data,
                    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    as_attachment=True,
                    download_name='kampanie_reklamowe.xlsx'
                )
                
            elif export_format == 'pdf':
                pdf_data = generate_pdf(
                    data, 
                    headers, 
                    f'Raport kampanii reklamowych',
                    orientation='landscape'
                )
                return send_file(
                    BytesIO(pdf_data.read()),
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name='kampanie_reklamowe.pdf'
                )
                
        except Exception as e:
            # Logowanie błędu
            print(f"Błąd w raporcie kampanii: {str(e)}")
            flash(f"Wystąpił błąd podczas generowania raportu: {str(e)}", "danger")
            
            # Przywrócenie formularza z danymi bez generowania raportu
            return render_template('reports/ad_campaigns.html', 
                                 data=[], 
                                 headers=[], 
                                 filters=filters,
                                 clients=clients)
    
    # Bezpieczne konwertowanie dat dla widoku
    start_date = None
    end_date = None
    
    try:
        if filters['start_date'] and filters['start_date'].strip():
            start_date = datetime.strptime(filters['start_date'], '%Y-%m-%d').date()
            
        if filters['end_date'] and filters['end_date'].strip():
            end_date = datetime.strptime(filters['end_date'], '%Y-%m-%d').date()
    except ValueError as e:
        flash(f"Nieprawidłowy format daty: {str(e)}", "warning")
        
    # Generowanie danych raportu dla widoku
    try:
        data, headers = get_ad_campaigns_report(start_date, end_date, filters['client'])
    except Exception as e:
        print(f"Błąd podczas generowania danych: {str(e)}")
        flash("Nie można wygenerować raportu z podanymi parametrami", "warning")
        data = []
        headers = []
    
    return render_template('reports/ad_campaigns.html', 
                          data=data, 
                          headers=headers, 
                          filters=filters,
                          clients=clients)