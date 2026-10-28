from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from .models import Equipment, Booking
from .forms import BookingForm


def is_manager(user):
    return user.is_staff  # для простоты: staff = менеджер/админ


def catalog(request):
    equipment = Equipment.objects.filter(status='available')
    return render(request, 'rental/catalog.html', {'equipment': equipment})


@login_required
def book_equipment(request, equipment_id):
    equipment = get_object_or_404(Equipment, id=equipment_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            messages.success(request, "Бронь создана. Ожидайте подтверждения менеджера.")
            return redirect('my_bookings')
    else:
        form = BookingForm(initial={'equipment': equipment, 'quantity': 1})
    
    return render(request, 'rental/book_form.html', {'form': form, 'equipment': equipment})


@login_required
def my_bookings(request):
    bookings = request.user.bookings.all().order_by('-created_at')
    return render(request, 'rental/my_bookings.html', {'bookings': bookings})


@user_passes_test(is_manager)
def manager_panel(request):
    bookings = Booking.objects.all().order_by('-created_at')
    return render(request, 'rental/manager.html', {'bookings': bookings})


@user_passes_test(is_manager)
def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.status == 'pending':
        booking.status = 'confirmed'
        booking.save()
        messages.success(request, f"Бронь #{booking.id} подтверждена")
    return redirect('manager_panel')


@user_passes_test(is_manager)
def issue_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.status == 'confirmed':
        booking.status = 'issued'
        booking.equipment.status = 'rented'  # упрощённо: помечаем всё оборудование
        booking.equipment.save()
        booking.save()
        messages.success(request, f"Оборудование выдано по брони #{booking.id}")
    return redirect('manager_panel')


@user_passes_test(is_manager)
def return_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if booking.status not in ['issued', 'overdue']:
        messages.error(request, "Эту бронь нельзя вернуть (статус не 'выдано')")
        return redirect('manager_panel')
    
    today = timezone.now().date()
    if today > booking.end_date:
        # штраф: 10% от стоимости за каждый день просрочки
        days_late = (today - booking.end_date).days
        booking.fine = booking.total_price * 0.1 * days_late
        booking.status = 'overdue'
    else:
        booking.status = 'returned'
    
    # Упрощённо: возвращаем оборудование в доступные (если не списано)
    if booking.equipment.status == 'rented':
        booking.equipment.status = 'available'
        booking.equipment.save()
    
    booking.save()
    messages.success(request, f"Возврат оформлен. Штраф: {booking.fine} руб.")
    return redirect('manager_panel')