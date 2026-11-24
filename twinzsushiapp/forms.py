
from django import forms
from django.forms import inlineformset_factory

from .models import (
    Order, OrderItem, Reservation
)


# In-store Order Form
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer', 'employee']


# Sushi Item Form
class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity']


# Multiple Sushi Items
OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=3,
    can_delete=True
)


# Edit Incoming Reservation
class ReservationEditForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = [
            'delivery_option',
            'reservation_date',
            'reservation_time',
            'payment_method',
            'downpayment_amount',
            'reservation_status'
        ]

        widgets = {
            'reservation_date': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'reservation_time': forms.TimeInput(
                attrs={'type': 'time'}
            ),
        }


# Update Order Progress
class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['order_status']


# Update Reservation Progress
class ReservationStatusForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['reservation_status']