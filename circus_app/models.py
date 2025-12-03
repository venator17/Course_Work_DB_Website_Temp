#
# Повний шлях до файлу: C:\Users\count\Desktop\COURSE WORK\circus_project\circus_app\models.py
#

from django.db import models

# -----------------------------------------------------------------------------
# 🏛️ Основні сутності (Розділ 3.1)
# -----------------------------------------------------------------------------

class Artist(models.Model):
    # 'id' (PK) створюється автоматично
    full_name = models.CharField(max_length=255, verbose_name="Повне ім'я")
    role = models.CharField(max_length=100, help_text="Напр., клоун, акробат, дресирувальник", verbose_name="Роль")
    contract_details = models.TextField(null=True, blank=True, verbose_name="Деталі контракту")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Час створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Час оновлення")

    def __str__(self):
        return f"{self.full_name} ({self.role})"
        
    class Meta:
        verbose_name = "Артист"
        verbose_name_plural = "Артисти"


class Animal(models.Model):
    trainer = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Тренер (Артист)")
    name = models.CharField(max_length=255, verbose_name="Кличка")
    species = models.CharField(max_length=100, verbose_name="Вид")
    medical_records = models.TextField(null=True, blank=True, verbose_name="Медичні записи")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Час створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Час оновлення")

    def __str__(self):
        return f"{self.name} ({self.species})"

    class Meta:
        verbose_name = "Тварина"
        verbose_name_plural = "Тварини"


class Inventory(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва предмета")
    type = models.CharField(max_length=100, help_text="Напр., костюм, реквізит, обладнання", verbose_name="Тип")
    condition = models.CharField(max_length=100, null=True, blank=True, verbose_name="Стан")
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name="Місцезнаходження")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Час створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Час оновлення")

    def __str__(self):
        return f"{self.name} ({self.type})"

    class Meta:
        verbose_name = "Інвентар"
        verbose_name_plural = "Інвентар"


class Show(models.Model):
    program_name = models.CharField(max_length=255, verbose_name="Назва програми")
    show_datetime = models.DateTimeField(verbose_name="Дата та час вистави")
    duration_minutes = models.IntegerField(null=True, blank=True, verbose_name="Тривалість (хв)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Час створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Час оновлення")
    
    # Зв'язок "багато-до-багатьох" з Номерами (Acts) через проміжну таблицю ShowAct
    acts = models.ManyToManyField('Act', through='ShowAct', verbose_name="Номери програми")

    def __str__(self):
        return f"{self.program_name} ({self.show_datetime.strftime('%Y-%m-%d %H:%M')})"

    class Meta:
        verbose_name = "Вистава"
        verbose_name_plural = "Вистави"
        ordering = ['-show_datetime'] # Сортувати за датою (новіші спочатку)


class Act(models.Model):
    name = models.CharField(max_length=255, verbose_name="Назва номеру")
    description = models.TextField(null=True, blank=True, verbose_name="Опис")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Час створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Час оновлення")
    
    # Зв'язки "багато-до-багатьох"
    artists = models.ManyToManyField(Artist, through='ActArtist', verbose_name="Артисти")
    animals = models.ManyToManyField(Animal, through='ActAnimal', blank=True, verbose_name="Тварини")
    inventory = models.ManyToManyField(Inventory, through='ActInventory', blank=True, verbose_name="Інвентар")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Номер (Акт)"
        verbose_name_plural = "Номери (Акти)"


class Seat(models.Model):
    sector = models.CharField(max_length=50, verbose_name="Сектор")
    row_number = models.CharField(max_length=10, verbose_name="Ряд")
    seat_number = models.CharField(max_length=10, verbose_name="Місце")
    price_category = models.CharField(max_length=50, default='standard', verbose_name="Категорія ціни")

    class Meta:
        # Унікальність гарантує, що не буде двох однакових місць
        unique_together = ('sector', 'row_number', 'seat_number')
        verbose_name = "Місце"
        verbose_name_plural = "Місця"
        ordering = ['sector', 'row_number', 'seat_number']

    def __str__(self):
        return f"Сектор {self.sector}, Ряд {self.row_number}, Місце {self.seat_number}"


class Ticket(models.Model):
    STATUS_CHOICES = [
        ('available', 'У продажу'),
        ('reserved', 'Заброньовано'),
        ('sold', 'Продано'),
    ]
    
    show = models.ForeignKey(Show, on_delete=models.CASCADE, verbose_name="Вистава")
    seat = models.ForeignKey(Seat, on_delete=models.PROTECT, verbose_name="Місце") # PROTECT забороняє видаляти місце, якщо на нього є квиток
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ціна")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='available', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Час створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Час оновлення")

    class Meta:
        # Квиток на одне місце на одну виставу має бути унікальним
        unique_together = ('show', 'seat')
        verbose_name = "Квиток"
        verbose_name_plural = "Квитки"

    def __str__(self):
        return f"Квиток №{self.id} на '{self.show.program_name}' ({self.get_status_display()})"


# -----------------------------------------------------------------------------
# 🔗 Під-сутності (Проміжні таблиці для зв'язків "багато-до-багатьох")
# -----------------------------------------------------------------------------

class ShowAct(models.Model):
    show = models.ForeignKey(Show, on_delete=models.CASCADE, verbose_name="Вистава")
    act = models.ForeignKey(Act, on_delete=models.CASCADE, verbose_name="Номер (Акт)")
    act_order = models.IntegerField(null=True, blank=True, verbose_name="Порядок виступу")

    class Meta:
        verbose_name = "Номер у виставі"
        verbose_name_plural = "Номери у виставах"
        ordering = ['act_order']


class ActArtist(models.Model):
    act = models.ForeignKey(Act, on_delete=models.CASCADE, verbose_name="Номер (Акт)")
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, verbose_name="Артист")

    class Meta:
        verbose_name = "Артист у номері"
        verbose_name_plural = "Артисти у номерах"


class ActAnimal(models.Model):
    act = models.ForeignKey(Act, on_delete=models.CASCADE, verbose_name="Номер (Акт)")
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, verbose_name="Тварина")

    class Meta:
        verbose_name = "Тварина у номері"
        verbose_name_plural = "Тварини у номерах"


class ActInventory(models.Model):
    act = models.ForeignKey(Act, on_delete=models.CASCADE, verbose_name="Номер (Акт)")
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, verbose_name="Інвентар")
    quantity = models.IntegerField(default=1, verbose_name="Кількість")
    
    class Meta:
        verbose_name = "Інвентар для номера"
        verbose_name_plural = "Інвентар для номерів"