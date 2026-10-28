from django.urls import path
from . import views

urlpatterns = [
    path('', views.catalog, name='catalog'),
    path('book/<int:equipment_id>/', views.book_equipment, name='book_equipment'),
    path('my/', views.my_bookings, name='my_bookings'),
    path('manager/', views.manager_panel, name='manager_panel'),
    path('manager/confirm/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
    path('manager/issue/<int:booking_id>/', views.issue_booking, name='issue_booking'),
    path('manager/return/<int:booking_id>/', views.return_booking, name='return_booking'),
]