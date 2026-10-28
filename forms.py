from django import forms
from .models import Booking
from django.core.exceptions import ValidationError


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['equipment', 'quantity', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned = super().clean()
        equipment = cleaned.get('equipment')
        quantity = cleaned.get('quantity')
        start = cleaned.get('start_date')
        end = cleaned.get('end_date')

        if not all([equipment, quantity, start, end]):
            return cleaned

        if start >= end:
            raise ValidationError("Дата возврата должна быть позже даты выдачи")

        overlapping = Booking.objects.filter(
            equipment=equipment,
            status__in=['pending', 'confirmed', 'issued'],
            start_date__lt=end,
            end_date__gt=start,
        )
        busy_count = sum(b.quantity for b in overlapping)
        available = equipment.quantity - busy_count

        if quantity > available:
            raise ValidationError(
                f"На выбранные даты доступно только {available} ед. "
                f"(запрошено {quantity})."
            )
        return cleaned