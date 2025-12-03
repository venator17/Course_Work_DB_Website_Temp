import csv
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.db.models import Count, Q
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Show, Ticket, Inventory, Act, ShowAct

# ... (ваші існуючі функції home_page, show_details, buy_ticket залишаються без змін) ...

def home_page(request):
    """Головна сторінка з афішею"""
    upcoming_shows = Show.objects.filter(
        show_datetime__gte=timezone.now()
    ).order_by('show_datetime')[:6]
    
    return render(request, 'circus_app/home.html', {'latest_shows': upcoming_shows})

def show_details(request, show_id):
    """Детальна сторінка вистави + покупка квитків"""
    show = get_object_or_404(Show, id=show_id)
    
    # Отримуємо номери (акти)
    acts = show.showact_set.select_related('act').order_by('act_order')
    
    # Отримуємо квитки, групуючи їх по секторах для зручності відображення
    tickets = show.ticket_set.all().select_related('seat').order_by('seat__row_number', 'seat__seat_number')
    
    return render(request, 'circus_app/show_details.html', {
        'show': show,
        'acts': acts,
        'tickets': tickets
    })

@require_POST
def buy_ticket(request, ticket_id):
    """Обробка купівлі квитка"""
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if ticket.status == 'available':
        ticket.status = 'sold'
        ticket.save()
        messages.success(request, f"Ви успішно купили квиток: Сектор {ticket.seat.sector}, Місце {ticket.seat.seat_number}")
    else:
        messages.error(request, "На жаль, цей квиток вже зайнятий.")
    
    return redirect('show_details', show_id=ticket.show.id)


# --- ЗВІТ 1: КВИТКИ ---

def ticket_report(request):
    """Звіт по квитках (перегляд)"""
    shows_stats = Show.objects.annotate(
        total_tickets=Count('ticket'),
        sold_tickets=Count('ticket', filter=Q(ticket__status='sold')),
        reserved_tickets=Count('ticket', filter=Q(ticket__status='reserved')),
        available_tickets=Count('ticket', filter=Q(ticket__status='available'))
    ).order_by('-show_datetime')

    return render(request, 'circus_app/reports/ticket_report.html', {'shows_stats': shows_stats})

def export_ticket_report_csv(request):
    """Експорт звіту по квитках в CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="ticket_report.csv"'
    response.write(u'\ufeff'.encode('utf8')) # BOM для коректного відкриття в Excel

    writer = csv.writer(response)
    writer.writerow(['Вистава', 'Дата', 'Всього місць', 'Продано', 'Бронь', 'Вільно'])

    shows_stats = Show.objects.annotate(
        total_tickets=Count('ticket'),
        sold_tickets=Count('ticket', filter=Q(ticket__status='sold')),
        reserved_tickets=Count('ticket', filter=Q(ticket__status='reserved')),
        available_tickets=Count('ticket', filter=Q(ticket__status='available'))
    ).order_by('-show_datetime')

    for show in shows_stats:
        writer.writerow([
            show.program_name,
            show.show_datetime.strftime("%d.%m.%Y %H:%M"),
            show.total_tickets,
            show.sold_tickets,
            show.reserved_tickets,
            show.available_tickets
        ])

    return response


# --- ЗВІТ 2: ВИСТАВИ ТА НОМЕРИ ---

def show_acts_report(request):
    """Звіт по виставах і номерах (перегляд)"""
    # Отримуємо всі зв'язки Вистава-Номер, підтягуючи дані про виставу і номер
    show_acts = ShowAct.objects.select_related('show', 'act').prefetch_related('act__artists').order_by('show__show_datetime', 'act_order')
    
    return render(request, 'circus_app/reports/show_acts_report.html', {'show_acts': show_acts})

def export_show_acts_report_csv(request):
    """Експорт звіту по виставах і номерах в CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="show_acts_report.csv"'
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response)
    writer.writerow(['Вистава', 'Дата', 'Порядок', 'Номер', 'Опис', 'Артисти'])

    show_acts = ShowAct.objects.select_related('show', 'act').prefetch_related('act__artists').order_by('show__show_datetime', 'act_order')

    for sa in show_acts:
        artists = ", ".join([artist.full_name for artist in sa.act.artists.all()])
        writer.writerow([
            sa.show.program_name,
            sa.show.show_datetime.strftime("%d.%m.%Y %H:%M"),
            sa.act_order,
            sa.act.name,
            sa.act.description,
            artists
        ])

    return response


# --- ЗВІТ 3: ІНВЕНТАР ---

def inventory_report(request):
    """Звіт по інвентарю (перегляд)"""
    inventory_list = Inventory.objects.prefetch_related('actinventory_set__act').all()
    return render(request, 'circus_app/reports/inventory_report.html', {'inventory_list': inventory_list})

def export_inventory_report_csv(request):
    """Експорт звіту по інвентарю в CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="inventory_report.csv"'
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response)
    writer.writerow(['Предмет', 'Тип', 'Стан', 'Місцезнаходження', 'Використовується в номерах'])

    inventory_list = Inventory.objects.prefetch_related('actinventory_set__act').all()

    for item in inventory_list:
        usages = [f"{u.act.name} ({u.quantity} шт.)" for u in item.actinventory_set.all()]
        usage_str = "; ".join(usages) if usages else "Не задіяний"
        
        writer.writerow([
            item.name,
            item.type,
            item.condition,
            item.location,
            usage_str
        ])

    return response