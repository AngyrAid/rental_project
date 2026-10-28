from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Equipment(models.Model):
    STATUS_CHOICES = [
        ('available', 'Доступно'),
        ('rented', 'В аренде'),
        ('repair', 'В ремонте'),
        ('written_off', 'Списано'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Название")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория")
    description = models.TextField(blank=True, verbose_name="Описание")
    price_per_day = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за сутки")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество единиц")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available', verbose_name="Статус")
    image = models.ImageField(upload_to='equipment/', blank=True, null=True, verbose_name="Фото")
    
    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"
    
    def available_quantity(self, start_date, end_date, exclude_booking_id=None):
        """Сколько единиц свободно на указанный период."""
        bookings = self.bookings.filter(
            status__in=['confirmed', 'issued'],
            start_date__lt=end_date,
            end_date__gt=start_date,
        )
        if exclude_booking_id:
            bookings = bookings.exclude(id=exclude_booking_id)
        busy = sum(b.quantity for b in bookings)
        return max(0, self.quantity - busy)
    
    class Meta:
        verbose_name = "Оборудование"
        verbose_name_plural = "Оборудование"


class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждено'),
        ('issued', 'Выдано'),
        ('returned', 'Возвращено'),
        ('overdue', 'Просрочено'),
        ('cancelled', 'Отменено'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings', verbose_name="Клиент")
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, related_name='bookings', verbose_name="Оборудование")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    start_date = models.DateField(verbose_name="Дата начала")
    end_date = models.DateField(verbose_name="Дата окончания")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Итого")
    fine = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Штраф")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def clean(self):
        if self.start_date and self.end_date:
            if self.start_date >= self.end_date:
                raise ValidationError("Дата окончания должна быть позже даты начала")
            if self.start_date < timezone.now().date():
                raise ValidationError("Нельзя бронировать на прошедшую дату")
    
    def save(self, *args, **kwargs):
        if not self.total_price:
            days = (self.end_date - self.start_date).days
            self.total_price = self.equipment.price_per_day * days * self.quantity
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} → {self.equipment.name} ({self.start_date} — {self.end_date})"
    
    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"