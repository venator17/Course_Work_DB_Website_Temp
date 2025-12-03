from django.contrib import admin
from . import models

# Ми "реєструємо" кожну модель (таблицю) в адмін-панелі.
# Django автоматично створить для них інтерфейс (форми та звіти).

@admin.register(models.Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'role', 'created_at') # Які колонки показувати у звіті
    search_fields = ('full_name', 'role') # Додати пошук за цими полями

@admin.register(models.Animal)
class AnimalAdmin(admin.ModelAdmin):
    list_display = ('name', 'species', 'trainer', 'updated_at')
    search_fields = ('name', 'species')
    list_filter = ('species', 'trainer') # Додати фільтри збоку

@admin.register(models.Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'condition', 'location')
    search_fields = ('name',)
    list_filter = ('type', 'condition')

@admin.register(models.Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('program_name', 'show_datetime', 'duration_minutes')
    search_fields = ('program_name',)
    list_filter = ('show_datetime',)

@admin.register(models.Act)
class ActAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(models.Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('sector', 'row_number', 'seat_number', 'price_category')
    search_fields = ('sector',)
    list_filter = ('price_category',)

@admin.register(models.Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'show', 'seat', 'price', 'status', 'updated_at')
    search_fields = ('show__program_name', 'seat__sector')
    list_filter = ('status', 'show')
    list_editable = ('status', 'price') # Дозволяє редагувати прямо зі "звіту"

# Також реєструємо проміжні таблиці, щоб їх було видно
admin.site.register(models.ShowAct)
admin.site.register(models.ActArtist)
admin.site.register(models.ActAnimal)
admin.site.register(models.ActInventory)
