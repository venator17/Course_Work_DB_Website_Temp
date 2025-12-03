from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    
    # Деталі вистави та купівля
    path('show/<int:show_id>/', views.show_details, name='show_details'),
    path('ticket/<int:ticket_id>/buy/', views.buy_ticket, name='buy_ticket'),

    # --- ЗВІТИ ---
    
    # 1. Квитки
    path('reports/tickets/', views.ticket_report, name='ticket_report'),
    path('reports/tickets/csv/', views.export_ticket_report_csv, name='export_ticket_report_csv'),
    
    # 2. Вистави та Номери
    path('reports/shows/', views.show_acts_report, name='show_acts_report'),
    path('reports/shows/csv/', views.export_show_acts_report_csv, name='export_show_acts_report_csv'),

    # 3. Інвентар
    path('reports/inventory/', views.inventory_report, name='inventory_report'),
    path('reports/inventory/csv/', views.export_inventory_report_csv, name='export_inventory_report_csv'),
]