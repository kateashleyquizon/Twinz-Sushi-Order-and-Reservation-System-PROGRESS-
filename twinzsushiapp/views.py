from decimal import Decimal
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from .models import (
    Employee, Order, OrderItem, Reservation, Transaction
)

from .forms import (
    OrderForm, OrderItemFormSet,
    ReservationEditForm,
    OrderStatusForm, ReservationStatusForm
)


# WELCOME PAGE
def welcome(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    return render(request, 'twinzsushiapp/welcome.html')


# EMPLOYEE LOGIN
def employee_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = AuthenticationForm(
        request,
        data=request.POST or None
    )

    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('dashboard')

    return render(request, 'twinzsushiapp/login.html', {
        'form': form
    })


# EMPLOYEE LOGOUT
@login_required
def employee_logout(request):
    logout(request)
    return redirect('welcome')


# DASHBOARD
@login_required
def dashboard(request):
    orders = Order.objects.all().order_by('-order_date')
    reservations = Reservation.objects.all().order_by(
        '-reservation_date'
    )
    transactions = Transaction.objects.all()

    return render(request, 'twinzsushiapp/dashboard.html', {
        'orders': orders,
        'reservations': reservations,
        'transactions': transactions
    })


# ORDER MANAGEMENT
@login_required
def order_list(request):
    orders = Order.objects.filter(
        reservation__isnull=True
    ).order_by('-order_date')

    return render(request, 'twinzsushiapp/orders.html', {
        'orders': orders
    })


# CREATE IN-STORE ORDER
@login_required
def add_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            if not any(
                f.cleaned_data.get('menu_item')
                for f in formset.forms
                if f.cleaned_data and not f.cleaned_data.get('DELETE')
            ):
                form.add_error(
                    None, 'Please select at least one sushi item.'
                )
            else:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.reservation = None
                    order.save()

                    formset.instance = order
                    total = Decimal('0.00')

                    for item_form in formset.forms:
                        if not item_form.cleaned_data:
                            continue

                        if item_form.cleaned_data.get('DELETE'):
                            continue

                        menu_item = item_form.cleaned_data.get('menu_item')
                        quantity = item_form.cleaned_data.get('quantity')

                        if menu_item and quantity:
                            item = item_form.save(commit=False)
                            item.order = order
                            item.subtotal = menu_item.price * quantity
                            item.save()
                            total += item.subtotal

                    order.total_amount = total
                    order.save()

                    Transaction.objects.create(
                        order=order,
                        transaction_type='Order',
                        amount=total
                    )

                return redirect('orders')
    else:
        form = OrderForm()
        formset = OrderItemFormSet()

    return render(request, 'twinzsushiapp/order_form.html', {
        'form': form,
        'formset': formset
    })


# UPDATE ORDER PROGRESS
@login_required
def update_order(request, order_id):
    order = get_object_or_404(
        Order, id=order_id, reservation__isnull=True
    )

    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)

        if form.is_valid():
            form.save()
            return redirect('orders')
    else:
        form = OrderStatusForm(instance=order)

    return render(request, 'twinzsushiapp/status_form.html', {
        'form': form,
        'title': 'Update Order Progress',
        'back_url': 'orders'
    })


# RESERVATION LIST
@login_required
def reservation_list(request):
    reservations = Reservation.objects.all().order_by(
        '-reservation_date'
    )

    return render(request, 'twinzsushiapp/reservations.html', {
        'reservations': reservations
    })


# EDIT INCOMING RESERVATION

@login_required
def edit_reservation(request, reservation_id):
    reservation = get_object_or_404(
        Reservation, id=reservation_id
    )

    order = reservation.order_set.first()

    # Calculate the minimum 50% downpayment
    minimum_downpayment = (
        order.total_amount * Decimal('0.50')
        if order else Decimal('0.00')
    )

    if request.method == 'POST':
        form = ReservationEditForm(
            request.POST, instance=reservation
        )

        if form.is_valid():
            downpayment = form.cleaned_data['downpayment_amount']
            payment_method = form.cleaned_data['payment_method']

            if order:
                if downpayment > order.total_amount:
                    form.add_error(
                        'downpayment_amount',
                        'Downpayment cannot exceed the order total.'
                    )

                elif payment_method != 'COD' and downpayment < minimum_downpayment:
                    form.add_error(
                        'downpayment_amount',
                        'Online reservations require at least 50% downpayment.'
                    )

                else:
                    form.save()
                    save_reservation_payment(reservation, order)
                    return redirect('reservations')

            else:
                form.save()
                return redirect('reservations')

    else:
        form = ReservationEditForm(instance=reservation)

    return render(
        request,
        'twinzsushiapp/reservation_edit.html',
        {
            'form': form,
            'reservation': reservation,
            'order': order,

            # Pass the calculated amount to the HTML template
            'minimum_downpayment': minimum_downpayment,
        }
    )


# SAVE OR UPDATE RESERVATION DOWNPAYMENT TRANSACTION
def save_reservation_payment(reservation, order):
    amount = reservation.downpayment_amount

    if amount > 0:
        Transaction.objects.update_or_create(
            order=order,
            reservation=reservation,
            transaction_type='Reservation',
            defaults={'amount': amount}
        )
    else:
        Transaction.objects.filter(
            order=order,
            reservation=reservation,
            transaction_type='Reservation'
        ).delete()


# RESERVED ORDER MONITORING
@login_required
def reservation_orders(request):
    reservations = Reservation.objects.all().order_by(
        '-reservation_date'
    )

    return render(
        request,
        'twinzsushiapp/reservation_orders.html',
        {'reservations': reservations}
    )


# UPDATE RESERVATION PROGRESS
@login_required
def update_reservation(request, reservation_id):
    reservation = get_object_or_404(
        Reservation, id=reservation_id
    )

    if request.method == 'POST':
        form = ReservationStatusForm(
            request.POST, instance=reservation
        )

        if form.is_valid():
            form.save()
            return redirect('reservations')
    else:
        form = ReservationStatusForm(instance=reservation)

    return render(request, 'twinzsushiapp/status_form.html', {
        'form': form,
        'title': 'Update Reservation Status',
        'back_url': 'reservations'
    })


# TRANSACTION HISTORY
@login_required
def transaction_list(request):
    in_store_transactions = Transaction.objects.filter(
        transaction_type='Order'
    ).order_by('-transaction_date')

    reservation_transactions = Transaction.objects.filter(
        transaction_type='Reservation'
    ).order_by('-transaction_date')

    return render(request, 'twinzsushiapp/transactions.html', {
        'in_store_transactions': in_store_transactions,
        'reservation_transactions': reservation_transactions
    })