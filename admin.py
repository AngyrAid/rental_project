from django.contrib import admin
from .models import Category, Equipment, Booking


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price_per_day', 'quantity', 'status')
    list_filter = ('status', 'category')
    search_fields = ('name',)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'equipment', 'start_date', 'end_date', 'status', 'total_price', 'fine')
    list_filter = ('status', 'start_date')
